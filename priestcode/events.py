"""events.py — the transparent event stream.

The whole design principle of Priest Code is that NOTHING happens invisibly.
The agent core is a pure engine that does not know about terminals or Textual;
it emits a stream of typed events, and any frontend (the full-screen TUI, the
plain headless renderer, a test harness) consumes them. This is the same split
OpenCode makes between its server and its TUI — an event boundary — done as an
in-process stream so there is no server to run.

Every event is a small immutable dataclass. A frontend pattern-matches on type.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class Event:
    """Base marker. All events are dataclasses subclassing this."""


# ── lifecycle ────────────────────────────────────────────────────────
@dataclass
class TurnStarted(Event):
    """A new assistant turn began (one request to the model)."""
    step: int


@dataclass
class Thinking(Event):
    """The model is reasoning (reasoning_content stream), before any answer."""
    text: str


@dataclass
class AssistantText(Event):
    """A chunk of the assistant's visible reply (streamed)."""
    text: str


@dataclass
class TurnFinished(Event):
    """The model finished a turn. `had_tool_calls` says whether it acted."""
    step: int
    had_tool_calls: bool
    truncated: bool = False


# ── tool activity (the transparent core) ─────────────────────────────
@dataclass
class ToolStarted(Event):
    """A tool call is about to run. Args are shown to the operator."""
    call_id: str
    name: str
    args: Dict[str, Any] = field(default_factory=dict)
    summary: str = ""            # one-line human summary ("read src/app.py")


@dataclass
class ToolFinished(Event):
    """A tool call completed."""
    call_id: str
    name: str
    ok: bool
    summary: str = ""            # one-line result ("42 lines", "exit 0")
    output: str = ""             # full textual output (may be long)
    detail: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Diff(Event):
    """A file was created or edited — a unified-diff view for the operator."""
    path: str
    unified: str
    added: int = 0
    removed: int = 0
    created: bool = False


# ── approvals ────────────────────────────────────────────────────────
@dataclass
class ApprovalRequest(Event):
    """The agent needs a yes/no before a side effect (a shell command, etc).

    The frontend must call `respond(True/False)` on this object. The agent
    blocks on `future` until then. In headless/auto modes the runner answers.
    """
    kind: str                    # "shell" | "write" | ...
    prompt: str
    detail: str = ""
    _answer: Optional[bool] = None

    def respond(self, ok: bool) -> None:
        self._answer = bool(ok)


# ── notices / status ─────────────────────────────────────────────────
@dataclass
class Notice(Event):
    """A host-level message: a gate firing, a retry, a fallback, an error."""
    text: str
    level: str = "info"          # "info" | "warn" | "error" | "gate" | "ok"


@dataclass
class Usage(Event):
    """Token / timing stats for a turn."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    seconds: float = 0.0
    model: str = ""


@dataclass
class Done(Event):
    """The whole request settled — the agent is idle, waiting for input."""
    steps: int
    reason: str = "complete"     # "complete" | "max_steps" | "stopped" | "error"


@dataclass
class TodoUpdated(Event):
    """The task/todo list changed (mirrors OpenCode's todo panel)."""
    items: List[Dict[str, str]] = field(default_factory=list)
