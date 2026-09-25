"""render.py — the plain (non-fullscreen) renderer.

Consumes the agent's event stream and prints it as a clean, colored, scrolling
transcript with Rich. This is what `priest -p "…"` (headless / one-shot) uses,
and the fallback if the full-screen TUI cannot start. It is deliberately simple
and side-effect-only, so it is trivial to test by feeding it events.
"""

from __future__ import annotations

import sys

from . import events as E
from . import harness

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.text import Text
    _RICH = True
except Exception:                       # pragma: no cover
    _RICH = False


_ACCENT = "#d97757"      # coral
_VIOLET = "#a78bfa"
_DIM = "grey62"


class PlainRenderer:
    def __init__(self, console=None, show_thinking: bool = False):
        self.console = console or (Console() if _RICH else None)
        self.show_thinking = show_thinking
        self._buf = ""            # current assistant prose buffer
        self._thinking_started = False
        self.errored = False      # set if the run ends in an error (headless exit code)
        self._spent = 0.0         # running $ spent (from Usage totals)
        self._toks = 0            # running token total

    # the event sink handed to Agent.send
    def __call__(self, ev: E.Event) -> None:
        # track failure regardless of renderer, for the headless exit code
        if isinstance(ev, E.Notice) and ev.level == "error":
            self.errored = True
        elif isinstance(ev, E.Done) and ev.reason == "error":
            self.errored = True
        if not _RICH:
            self._plainest(ev)
            return
        c = self.console
        if isinstance(ev, E.AssistantText):
            self._buf += ev.text
        elif isinstance(ev, E.Thinking):
            if self.show_thinking:
                if not self._thinking_started:
                    c.print(Text("thinking…", style=f"italic {_DIM}"))
                    self._thinking_started = True
        elif isinstance(ev, E.TurnFinished):
            self._flush_prose()
            self._thinking_started = False
        elif isinstance(ev, E.ToolStarted):
            c.print(Text(f"  → {ev.summary or ev.name}", style=_VIOLET))
        elif isinstance(ev, E.ToolFinished):
            mark = "✓" if ev.ok else "✗"
            style = "green" if ev.ok else "red"
            c.print(Text(f"  {mark} {ev.summary or ev.name}", style=style))
            if ev.name == "run" and ev.output:
                c.print(Panel(ev.output[:4000], border_style=_DIM,
                              title="output", title_align="left"))
        elif isinstance(ev, E.Diff):
            self._print_diff(ev)
        elif isinstance(ev, E.Notice):
            if ev.level == "error":
                self.errored = True
            style = {"error": "red", "warn": "yellow", "ok": "green",
                     "gate": _ACCENT}.get(ev.level, _DIM)
            c.print(Text(f"  {ev.text}", style=style))
        elif isinstance(ev, E.TodoUpdated):
            self._print_todos(ev)
        elif isinstance(ev, E.Status):
            # a live one-liner of what's happening now (kept dim, transient)
            if ev.phase in ("tool", "skill", "subagent"):
                c.print(Text(f"  · {ev.text}", style=_DIM))
        elif isinstance(ev, E.Usage):
            self._spent = ev.total_cost_usd or self._spent
            self._toks = ev.total_tokens or self._toks
            if ev.completion_tokens or ev.seconds:
                cost = f" · ${ev.cost_usd:.4f}" if ev.cost_usd else ""
                c.print(Text(
                    f"    {ev.model} · {ev.completion_tokens} tok{cost} · "
                    f"{ev.seconds:.1f}s", style=_DIM))
        elif isinstance(ev, E.Done):
            if ev.reason == "error":
                self.errored = True
            self._flush_prose()
            if self._toks:
                spent = f" · ${self._spent:.4f} spent" if self._spent else ""
                c.print(Text(f"  ─ {self._toks:,} tokens{spent}", style=_DIM))

    def _flush_prose(self) -> None:
        text = harness.clean_reply(self._buf)
        self._buf = ""
        if text and _RICH:
            try:
                self.console.print(Markdown(text))
            except Exception:
                self.console.print(text)

    def _print_diff(self, ev: E.Diff) -> None:
        if not ev.unified:
            head = "created" if ev.created else "edited"
            self.console.print(Text(f"  {head} {ev.path}", style=_ACCENT))
            return
        self.console.print(Syntax(ev.unified, "diff", theme="ansi_dark",
                                  background_color="default"))

    def _print_todos(self, ev: E.TodoUpdated) -> None:
        glyph = {"done": "[green]✔[/]", "doing": f"[{_ACCENT}]▸[/]",
                 "todo": "[grey50]○[/]"}
        lines = [f"  {glyph.get(i['status'], '○')} {i['text']}"
                 for i in ev.items]
        if lines:
            self.console.print("\n".join(lines))

    def _plainest(self, ev: E.Event) -> None:   # pragma: no cover
        if isinstance(ev, E.AssistantText):
            sys.stdout.write(ev.text)
            sys.stdout.flush()
        elif isinstance(ev, E.ToolStarted):
            print(f"\n  -> {ev.summary or ev.name}")
        elif isinstance(ev, E.ToolFinished):
            print(f"  {'ok' if ev.ok else 'X'} {ev.summary or ev.name}")
        elif isinstance(ev, E.Notice):
            print(f"  {ev.text}")


def auto_approver(mode: str):
    """A non-interactive approver for headless runs."""
    def approve(kind, prompt, detail):
        return mode == "yolo"    # headless: only run shell if explicitly YOLO
    return approve


def interactive_approver(console=None):
    """A y/N approver for the plain renderer's REPL."""
    c = console or (Console() if _RICH else None)

    def approve(kind, prompt, detail):
        if _RICH:
            c.print(Text(f"  {prompt}", style=_ACCENT))
            c.print(Text(f"    {detail}", style=_DIM))
        else:
            print(f"  {prompt}\n    {detail}")
        try:
            ans = input("  run it? [y/N] ").strip().lower()
        except EOFError:
            return False
        return ans in ("y", "yes")
    return approve
