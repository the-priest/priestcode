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
                 agent_def=None, permissions=None, instructions: str = "",
                 skills=None, enable_subagents: bool = True):
        from . import agents as _agents
        from . import snapshots as _snap
        self.config = config
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.workspace = workspace
        self.agent_def = agent_def or _agents.get(config.agent,
                                                  _agents.from_config(config.agents))
        self.permissions = permissions
        self.instructions = instructions
        self.snapshots = _snap.SnapshotStack()
        self._mcp_tools: Dict[str, Tool] = {}
        self.enable_subagents = enable_subagents
        # Native (OpenCode-style) function-calling is the primary path: a real
        # `tools` schema goes out, structured tool_calls come back. Flips off for
        # the session if a provider rejects the tools field (then the text
        # protocol fallback carries the turn).
        self.native = True
        # the tool set is the agent/mode's (plan mode is read-only), plus any
        # explicit override, plus MCP tools merged in by the caller.
        self.tools = tools or self.agent_def.toolset()
        self.client = Client(provider, config.base_url(), api_key)

        # ── skills + subagents: load the library once, register their tools ──
        if skills is None:
            try:
                from . import skills as _skills
                skills = _skills.load_skills(workspace)
            except Exception:
                skills = {}
        self.skills = skills or {}
        self._extra_tools: Dict[str, Tool] = {}
        if self.skills:
            try:
                from .skills import SkillTool
                self._extra_tools["skill"] = SkillTool(self.skills)
            except Exception:
                pass
        if self.enable_subagents:
            try:
                from .subagents import TaskTool
                self._extra_tools["task"] = TaskTool(self._spawn_subagent)
            except Exception:
                pass
        # extra tools ride alongside the mode's toolset and survive mode switches
        self.tools.update(self._extra_tools)

        self.messages: List[Dict[str, str]] = [
            {"role": "system",
             "content": system_prompt(self.tools, str(workspace),
                                      self._extra_context())}]
        self._stop = False
        self._emit = None           # the current send()'s event sink (for subagents)
        self.todos: List[Dict[str, str]] = []
        self.cost_tokens = 0        # running completion-token total for the session
        self.prompt_tokens_total = 0
        self.completion_tokens_total = 0
        self.spent_usd = 0.0        # running $ spent this session

    # ── the system-prompt tail: agent role, instructions, skills, subagents ──
    def _extra_context(self) -> str:
        parts: List[str] = []
        if self.agent_def.system:
            parts.append("# Agent: " + self.agent_def.name + "\n"
                         + self.agent_def.system)
        if self.instructions:
            parts.append("# Project instructions (from AGENTS.md / config)\n"
                         + self.instructions)
        if self.skills:
            try:
                from .skills import skills_index
                parts.append("# Skills\n" + skills_index(self.skills))
            except Exception:
                pass
        if self.enable_subagents and "task" in self._extra_tools:
            try:
                from .subagents import registry_index
                parts.append("# Subagents\n" + registry_index())
            except Exception:
                pass
        return "\n\n".join(parts)

    # ── spawn a specialist subagent, run it headless, return its result ──
    def _spawn_subagent(self, spec, prompt: str, ctx) -> str:
        from .tools import default_tools
        from . import agents as _agents
        from . import events as _E
        allow = None if not spec.read_only else (
            "read_file", "list_dir", "tree", "glob", "grep", "todo")
        base = default_tools()
        child_tools = (base if allow is None
                       else {n: t for n, t in base.items() if n in allow})
        child_def = _agents.Agent(name=spec.name, description=spec.description,
                                  system=spec.system, tools=None)
        child = Agent(self.config, self.provider, self.model, self.api_key,
                      self.workspace, tools=child_tools, agent_def=child_def,
                      permissions=self.permissions, instructions=self.instructions,
                      skills=self.skills, enable_subagents=False)
        child.config = self.config
        # the subagent shares the parent's approval callback, so any write/run it
        # does is gated exactly like the parent's — no silent escalation.
        collected: List[str] = []
        parent_emit = getattr(self, "_emit", None)

        def _emit(ev):
            if isinstance(ev, _E.AssistantText):
                collected.append(ev.text)
            # surface the subagent's work to the parent UI so a long delegation
            # never looks frozen — the operator sees what the specialist is doing.
            if parent_emit is not None:
                if isinstance(ev, _E.ToolStarted):
                    parent_emit(_E.Status(
                        "subagent", f"↳ {spec.name}: {ev.summary or ev.name}"))
                elif isinstance(ev, _E.Diff):
                    parent_emit(ev)
                elif isinstance(ev, _E.Notice) and ev.level in ("warn", "error"):
                    parent_emit(_E.Notice(f"[{spec.name}] {ev.text}", ev.level))

        steps_before = self.config.max_steps
        try:
            self.config.max_steps = min(steps_before, getattr(spec, "steps", 14))
            child.send(prompt, _emit, ctx.approve)
        finally:
            self.config.max_steps = steps_before
        # roll the subagent's token/$ spend into the session meter
        self.spent_usd += child.spent_usd
        self.prompt_tokens_total += child.prompt_tokens_total
        self.completion_tokens_total += child.completion_tokens_total
        self.cost_tokens += child.cost_tokens
        if parent_emit is not None:
            parent_emit(_E.Usage(
                0, 0, 0.0, self.model.label, cost_usd=0.0,
                total_tokens=(self.prompt_tokens_total
                              + self.completion_tokens_total),
                total_cost_usd=self.spent_usd))
        out = "".join(collected).strip()
        # keep the handback compact
        if len(out) > 8000:
            out = out[:8000] + "\n… (subagent output truncated)"
        return out or "(the subagent produced no summary)"

    def stop(self) -> None:
        self._stop = True

    def _rebuild_system(self) -> None:
        self.messages[0]["content"] = system_prompt(
            self.tools, str(self.workspace), self._extra_context())

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
        self.tools.update(self._extra_tools)   # skill/task survive a mode switch
        self._rebuild_system()

    def undo(self) -> Optional[str]:
        return self.snapshots.undo()

    # ── one full request (may span many model turns) ─────────────────
    def send(self, user_text: str, emit: Emit, approve: Approve) -> None:
        from . import context as _context
        self._stop = False
        self._emit = emit           # subagents forward their activity here
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
            emit(E.Status("waiting", "waiting for the model…"))
            comp = self._one_turn(emit)
            if comp.error:
                emit(E.Notice(comp.error, "error"))
                emit(E.Done(steps, "error"))
                return
            if comp.tools_unsupported:
                self.native = False     # this provider ignores tools
            # ── running token + cost meter (this turn AND the session total) ──
            self.cost_tokens += comp.completion_tokens
            self.prompt_tokens_total += comp.prompt_tokens
            self.completion_tokens_total += comp.completion_tokens
            turn_cost = self.model.cost_usd(comp.prompt_tokens,
                                            comp.completion_tokens)
            self.spent_usd += turn_cost
            emit(E.Usage(comp.prompt_tokens, comp.completion_tokens,
                         comp.seconds, self.model.label,
                         cost_usd=turn_cost,
                         total_tokens=(self.prompt_tokens_total
                                       + self.completion_tokens_total),
                         total_cost_usd=self.spent_usd))

            # ── NATIVE PATH: structured tool_calls (the OpenCode contract) ──
            if comp.tool_calls:
                self.messages.append({
                    "role": "assistant",
                    "content": comp.text or None,
                    "tool_calls": [
                        {"id": c["id"], "type": "function",
                         "function": {"name": c["name"],
                                      "arguments": c["arguments"]}}
                        for c in comp.tool_calls]})
                emit(E.TurnFinished(steps, had_tool_calls=True,
                                    truncated=comp.truncated))
                empty_retries = 0
                for c in comp.tool_calls:
                    if self._stop:
                        emit(E.Done(steps, "stopped"))
                        return
                    call = _structured_to_call(c)
                    ok, output = self._dispatch(call, ctx, emit)
                    # round-trip as a role:"tool" message with the call id
                    self.messages.append({"role": "tool",
                                          "tool_call_id": c["id"],
                                          "content": output})
                continue

            # ── FALLBACK PATH: the text <tool> protocol ──
            calls = harness.parse_tool_calls(comp.text)
            clean = harness.clean_reply(comp.text)
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
            result_blocks: List[str] = []
            for call in calls:
                if self._stop:
                    emit(E.Done(steps, "stopped"))
                    return
                ok, output = self._dispatch(call, ctx, emit)
                status = "ok" if ok else "error"
                result_blocks.append(
                    f'<tool_result name="{call.name}" status="{status}">\n'
                    f'{output}\n</tool_result>')
            self.messages.append(
                {"role": "user", "content": "\n".join(result_blocks)})
        emit(E.Notice(f"hit the {self.config.max_steps}-step ceiling", "warn"))
        emit(E.Done(steps, "max_steps"))

    # ── one model turn (streamed) ────────────────────────────────────
    def _one_turn(self, emit: Emit) -> Completion:
        seen = {"tok": False, "reason": False}

        def on_token(t: str):
            if not seen["tok"]:
                seen["tok"] = True
                emit(E.Status("responding", "writing a reply…"))
            emit(E.AssistantText(t))

        def on_reasoning(t: str):
            if not seen["reason"]:
                seen["reason"] = True
                emit(E.Status("thinking", "reasoning…"))
            emit(E.Thinking(t))

        from .tools import tools_schema
        schema = tools_schema(self.tools) if self.native else None
        return self.client.stream(
            self.model, self.messages, on_token, on_reasoning,
            temperature=self.config.temperature, top_p=self.config.top_p,
            max_tokens=self.config.max_tokens, tools=schema,
            cancel=lambda: self._stop)

    # ── run one tool call; emit events; return (ok, model-facing output) ──
    def _dispatch(self, call, ctx: ToolContext, emit: Emit):
        cid = f"c{int(time.time() * 1000) % 100000}"
        tool = self.tools.get(call.name)
        if tool is None:
            emit(E.ToolStarted(cid, call.name, call.args, f"unknown: {call.name}"))
            emit(E.ToolFinished(cid, call.name, False, summary="unknown tool"))
            return (False, f"unknown tool {call.name!r}. "
                    f"Available: {', '.join(self.tools)}.")
        if call.raw:
            emit(E.ToolStarted(cid, call.name, {}, "unparseable arguments"))
            emit(E.ToolFinished(cid, call.name, False, summary="bad JSON"))
            return (False, "the arguments were not valid JSON. Re-send this "
                    "call with a valid JSON body.")

        # a live, specific status so the operator always sees what's happening
        _sum = tool.summarize(call.args)
        if call.name == "skill":
            emit(E.Status("skill", f"loading skill: {call.args.get('name') or _sum}"))
        elif call.name == "task":
            emit(E.Status("subagent", f"delegating to {call.args.get('agent', '?')}…"))
        elif call.name == "run":
            emit(E.Status("tool", f"running: {call.args.get('command', '')[:60]}"))
        else:
            emit(E.Status("tool", _sum))
        emit(E.ToolStarted(cid, call.name, call.args, _sum))
        try:
            res = tool.run(call.args, ctx)
        except Exception as e:  # a tool must never take the loop down
            emit(E.ToolFinished(cid, call.name, False, summary=f"crashed: {e}"))
            return (False, f"tool crashed: {e}")

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
        return (res.ok, res.output)


def _structured_to_call(c: Dict) -> "harness.ToolCall":
    """Turn a native {id,name,arguments} tool call into a harness.ToolCall,
    marking it raw if the JSON arguments do not parse."""
    import json as _json
    name = c.get("name", "")
    raw_args = c.get("arguments") or "{}"
    try:
        args = _json.loads(raw_args) if raw_args.strip() else {}
        if not isinstance(args, dict):
            args = {"value": args}
        return harness.ToolCall(name=name, args=args, raw=False)
    except Exception:
        return harness.ToolCall(name=name, args={"_raw": raw_args}, raw=True)
