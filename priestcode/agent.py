"""agent.py — the loop.

Provider-agnostic, frontend-agnostic. It holds the conversation, drives the
model with the streaming client, parses tool calls out of the reply, runs them,
feeds results back, and repeats until the model stops calling tools (the job is
done) or a bound is hit. Every step is emitted as an Event; the agent knows
nothing about terminals.

The gates are the few that were paid for in the Basilisk project, kept minimal:
  • an empty / degraded reply is retried a bounded number of times, and only
    then reported — never an infinite loop;
  • a write cut off at the token cap tells the model to CONTINUE with append,
    rather than silently losing the file;
  • a hard step ceiling.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

from . import events as E
from . import harness
from .client import Client, Completion
from .config import Config
from .prompts import system_prompt
from .providers import Model, Provider
from .tools import Tool, ToolContext, default_tools


Emit = Callable[[E.Event], None]
Approve = Callable[[str, str, str], bool]


class Agent:
    def __init__(self, config: Config, provider: Provider, model: Model,
                 api_key: str, workspace: Path,
                 tools: Optional[Dict[str, Tool]] = None,
                 agent_def=None, permissions=None, instructions: str = ""):
        from . import agents as _agents
        from . import snapshots as _snap
        self.config = config
        self.provider = provider
        self.model = model
        self.workspace = workspace
        self.agent_def = agent_def or _agents.get(config.agent,
                                                  _agents.from_config(config.agents))
        self.permissions = permissions
        self.instructions = instructions
        self.snapshots = _snap.SnapshotStack()
        self._mcp_tools: Dict[str, Tool] = {}
        # the tool set is the agent/mode's (plan mode is read-only), plus any
        # explicit override, plus MCP tools merged in by the caller.
        self.tools = tools or self.agent_def.toolset()
        self.client = Client(provider, config.base_url(), api_key)
        extra = ""
        if self.agent_def.system:
            extra += "# Agent: " + self.agent_def.name + "\n" + self.agent_def.system
        if instructions:
            extra += ("\n\n# Project instructions (from AGENTS.md / config)\n"
                      + instructions)
        self.messages: List[Dict[str, str]] = [
            {"role": "system",
             "content": system_prompt(self.tools, str(workspace), extra)}]
        self._stop = False
        self.todos: List[Dict[str, str]] = []
        self.cost_tokens = 0        # running completion-token total for the session

    def stop(self) -> None:
        self._stop = True

    def _rebuild_system(self) -> None:
        extra = ""
        if self.agent_def.system:
            extra += "# Agent: " + self.agent_def.name + "\n" + self.agent_def.system
        if self.instructions:
            extra += "\n\n# Project instructions\n" + self.instructions
        self.messages[0]["content"] = system_prompt(
            self.tools, str(self.workspace), extra)

    def add_tools(self, extra: Dict[str, Tool]) -> None:
        """Merge in extra tools (e.g. MCP) and rebuild the system prompt so the
        model is told about them."""
        if not extra:
            return
        self._mcp_tools.update(extra)
        self.tools.update(extra)
        self._rebuild_system()

    def set_agent(self, agent_def) -> None:
        """Switch mode (build/plan/custom) at runtime: swap the tool set (plan
        is read-only) and rebuild the system prompt, keeping any MCP tools."""
        self.agent_def = agent_def
        self.config.agent = agent_def.name
        self.tools = agent_def.toolset()
        self.tools.update(self._mcp_tools)
        self._rebuild_system()

    def undo(self) -> Optional[str]:
        return self.snapshots.undo()

    # ── one full request (may span many model turns) ─────────────────
    def send(self, user_text: str, emit: Emit, approve: Approve) -> None:
        from . import context as _context
        self._stop = False
        user_text = _context.expand_mentions(user_text, self.workspace)
        self.messages.append({"role": "user", "content": user_text})
        ctx = ToolContext(cwd=self.workspace, approve=approve,
                          approval_mode=self.config.approval,
                          permissions=self.permissions)
        steps = 0
        empty_retries = 0
        while steps < self.config.max_steps:
            if self._stop:
                emit(E.Done(steps, "stopped"))
                return
            steps += 1
            emit(E.TurnStarted(steps))
            comp = self._one_turn(emit)
            if comp.error:
                emit(E.Notice(comp.error, "error"))
                emit(E.Done(steps, "error"))
                return
            self.cost_tokens += comp.completion_tokens
            emit(E.Usage(comp.prompt_tokens, comp.completion_tokens,
                         comp.seconds, self.model.label))

            calls = harness.parse_tool_calls(comp.text)
            clean = harness.clean_reply(comp.text)

            # record the assistant turn (canonical form, so history is clean)
            self.messages.append(
                {"role": "assistant",
                 "content": harness.canonicalise(comp.text) or clean})

            if not calls:
                # empty / degraded → bounded retry
                if not clean and comp.finish_reason not in ("stop", ""):
                    if empty_retries < 2:
                        empty_retries += 1
                        emit(E.Notice(
                            f"empty reply — retrying ({empty_retries}/2)", "warn"))
                        self.messages.append({
                            "role": "user",
                            "content": "[system] your last reply was empty. "
                            "If the task needs work, emit the tool call now; "
                            "if it is done, give the final summary."})
                        continue
                # a real prose answer → the turn is finished
                emit(E.TurnFinished(steps, had_tool_calls=False,
                                    truncated=comp.truncated))
                emit(E.Done(steps, "complete"))
                return

            emit(E.TurnFinished(steps, had_tool_calls=True,
                                truncated=comp.truncated))
            empty_retries = 0
            # run every call, collect results, feed them back as ONE user msg
            result_blocks: List[str] = []
            for call in calls:
                if self._stop:
                    emit(E.Done(steps, "stopped"))
                    return
                block = self._dispatch(call, ctx, emit)
                result_blocks.append(block)
            self.messages.append(
                {"role": "user", "content": "\n".join(result_blocks)})
        emit(E.Notice(f"hit the {self.config.max_steps}-step ceiling", "warn"))
        emit(E.Done(steps, "max_steps"))

    # ── one model turn (streamed) ────────────────────────────────────
    def _one_turn(self, emit: Emit) -> Completion:
        def on_token(t: str):
            emit(E.AssistantText(t))

        def on_reasoning(t: str):
            emit(E.Thinking(t))

        return self.client.stream(
            self.model, self.messages, on_token, on_reasoning,
            temperature=self.config.temperature, top_p=self.config.top_p,
            max_tokens=self.config.max_tokens,
            cancel=lambda: self._stop)

    # ── run one tool call, return the <tool_result> block for history ─
    def _dispatch(self, call, ctx: ToolContext, emit: Emit) -> str:
        cid = f"c{int(time.time() * 1000) % 100000}"
        tool = self.tools.get(call.name)
        if tool is None:
            emit(E.ToolStarted(cid, call.name, call.args, f"unknown: {call.name}"))
            emit(E.ToolFinished(cid, call.name, False,
                                summary="unknown tool"))
            return (f'<tool_result name="{call.name}">\nunknown tool '
                    f'{call.name!r}. Available: {", ".join(self.tools)}.\n'
                    f'</tool_result>')
        if call.raw:
            emit(E.ToolStarted(cid, call.name, {}, "unparseable arguments"))
            emit(E.ToolFinished(cid, call.name, False, summary="bad JSON"))
            return (f'<tool_result name="{call.name}">\nthe arguments were not '
                    f'valid JSON. Re-send this call with a valid JSON body.\n'
                    f'</tool_result>')

        emit(E.ToolStarted(cid, call.name, call.args, tool.summarize(call.args)))
        try:
            res = tool.run(call.args, ctx)
        except Exception as e:  # a tool must never take the loop down
            emit(E.ToolFinished(cid, call.name, False, summary=f"crashed: {e}"))
            return (f'<tool_result name="{call.name}">\ntool crashed: {e}\n'
                    f'</tool_result>')

        # snapshot the pre-change state so /undo can revert it
        if res.ok and call.name in ("write_file", "edit_file") and res.detail.get("path"):
            try:
                self.snapshots.push(Path(res.detail["path"]),
                                    res.detail.get("old"),
                                    label=(res.diff or {}).get("path", ""))
            except Exception:
                pass
        if res.diff:
            emit(E.Diff(res.diff["path"], res.diff["unified"],
                        res.diff["added"], res.diff["removed"],
                        res.diff["created"]))
        if call.name == "todo" and res.detail.get("items") is not None:
            self.todos = res.detail["items"]
            emit(E.TodoUpdated(self.todos))
        emit(E.ToolFinished(cid, call.name, res.ok, res.summary, res.output,
                            res.detail))
        status = "ok" if res.ok else "error"
        return (f'<tool_result name="{call.name}" status="{status}">\n'
                f'{res.output}\n</tool_result>')
