"""app.py — the full-screen Priest Code terminal application (Textual).

Design: an append-only transcript (RichLog) that shows EVERYTHING transparently
— the model's answer as markdown, every tool call the moment it starts, its
result and (for edits) a coloured unified diff, a live task panel, and a status
line naming exactly what the agent is doing. The agent runs on a worker thread
and marshals events to the UI thread; shell commands raise an approval modal.

Everything is driven by Textual's native theme system, so ctrl+p → "Change
theme" re-tints the whole app live, and the command palette (ctrl+p) offers a
model picker, approval-mode switch, and more — a real palette, not just slash
commands (those work too).
"""

from __future__ import annotations

import threading
import time
from pathlib import Path
from typing import Iterable

from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text

from textual import work
from textual.app import App, ComposeResult, SystemCommand
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Input, OptionList, RichLog, Static
from textual.widgets.option_list import Option

from .. import events as E
from .. import harness
from .. import providers as P
from ..agent import Agent
from . import theme as _theme


CSS = """
Screen { background: $background; color: $foreground; layers: base overlay; }
#header {
    height: 3; padding: 0 2; background: $surface;
    border-bottom: solid $primary 40%;
    content-align: left middle;
}
#body { height: 1fr; }
#log {
    width: 1fr; height: 1fr; padding: 0 2; background: $background;
    scrollbar-color: $panel; scrollbar-background: $background;
}
#todo {
    width: 32; height: 1fr; padding: 1 2; background: $surface;
    border-left: solid $panel; color: $foreground; display: none;
}
#todo.show { display: block; }
#status { height: 1; padding: 0 2; background: $surface; color: $text-muted; }
#prompt {
    border: tall $panel; background: $panel; color: $foreground;
    padding: 0 1; margin: 0 1 1 1;
}
#prompt:focus { border: tall $primary; }

ApproveModal { align: center middle; }
#dialog {
    width: 78; max-width: 90%; padding: 1 2; background: $panel;
    border: round $primary; height: auto;
}
#dialog .q { color: $primary; text-style: bold; }
#dialog .hint { color: $text-muted; }

PickerModal { align: center middle; }
#picker {
    width: 84; max-width: 92%; height: auto; max-height: 80%;
    background: $panel; border: round $primary; padding: 1 1;
}
#picker-title { color: $primary; text-style: bold; padding: 0 1 1 1; }
OptionList { background: $panel; }
OptionList > .option-list--option-highlighted {
    background: $primary 25%; color: $foreground; text-style: bold;
}
"""


class ApproveModal(ModalScreen):
    """A y/N confirmation for a side effect (a shell command)."""

    BINDINGS = [("y", "yes", "Yes"), ("n", "no", "No"), ("escape", "no", "No")]

    def __init__(self, prompt: str, detail: str):
        super().__init__()
        self._prompt = prompt
        self._detail = detail

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Static(Text(self._prompt), classes="q")
            yield Static(Text(self._detail))
            yield Static(Text("[y] run    [n] skip    (esc = skip)"),
                         classes="hint")

    def action_yes(self) -> None:
        self.dismiss(True)

    def action_no(self) -> None:
        self.dismiss(False)


class PickerModal(ModalScreen):
    """A generic searchable list picker (model, approval mode, …)."""

    BINDINGS = [("escape", "cancel", "cancel")]

    def __init__(self, title: str, options, on_pick):
        super().__init__()
        self._title = title
        self._options = options          # list[(id, Text/label)]
        self._on_pick = on_pick

    def compose(self) -> ComposeResult:
        with Vertical(id="picker"):
            yield Static(Text(self._title), id="picker-title")
            ol = OptionList(*[Option(label, id=oid)
                              for oid, label in self._options])
            yield ol

    def on_mount(self) -> None:
        self.query_one(OptionList).focus()

    def on_option_list_option_selected(self, ev: OptionList.OptionSelected):
        self.dismiss(ev.option.id)

    def action_cancel(self) -> None:
        self.dismiss(None)


class PriestApp(App):
    TITLE = "Priest Code"
    CSS = CSS

    BINDINGS = [
        ("ctrl+c", "quit", "quit"),
        ("ctrl+q", "quit", "quit"),
        ("ctrl+t", "toggle_todo", "tasks"),
        ("ctrl+o", "pick_model", "model"),
        ("ctrl+z", "undo", "undo"),
        ("escape", "interrupt", "stop"),
    ]

    def __init__(self, agent: Agent, theme_name: str = "priest"):
        super().__init__()
        self.agent = agent
        self._start_theme = theme_name if theme_name in _theme.BY_NAME else "priest"
        self._busy = False
        self._prose = ""            # unflushed tail of the streaming reply
        self._streamed = False      # did we already stream this turn's prose live?
        self._todos = []
        # live-activity state for the status bar (so it never looks frozen)
        self._phase = "ready"       # what's happening right now
        self._t0 = 0.0              # when the current request started
        self._spin = 0              # spinner frame index
        self._tokens = 0            # running session token total
        self._cost = 0.0            # running session $ spent
        for th in _theme.ALL:
            self.register_theme(th)

    _SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"

    # ── theming ──────────────────────────────────────────────────────
    def _col(self) -> dict:
        """Current theme colours as hex, for the Rich transcript."""
        t = self.current_theme
        v = t.variables or {}
        return {"accent": t.primary, "accent2": t.secondary,
                "ok": t.success, "warn": t.warning, "err": t.error,
                "fg": t.foreground, "dim": v.get("pc-dim", "#888888"),
                "user": v.get("pc-user", t.secondary)}

    # ── layout ───────────────────────────────────────────────────────
    def compose(self) -> ComposeResult:
        yield Static("", id="header")
        with Horizontal(id="body"):
            yield RichLog(id="log", wrap=True, markup=False, highlight=False,
                          auto_scroll=True)
            yield Static("", id="todo")
        yield Static("ready", id="status")
        yield Input(placeholder="ask, or describe the change…   "
                    "(ctrl+p palette · ctrl+o model · ctrl+t tasks · esc stops)",
                    id="prompt")

    def on_mount(self) -> None:
        self.theme = self._start_theme
        self.query_one("#header", Static).update(self._header_text())
        self.query_one("#prompt", Input).focus()
        self._banner()
        # a 10fps heartbeat: while the agent is busy this animates the spinner
        # and elapsed time so the UI is visibly alive even between events.
        self.set_interval(0.1, self._tick)

    def _tick(self) -> None:
        if not self._busy:
            return
        self._spin = (self._spin + 1) % len(self._SPINNER)
        self._render_status()

    def _render_status(self) -> None:
        """The live status line: spinner · what's happening · elapsed · meter."""
        c = self._col()
        meter = ""
        if self._tokens:
            meter = f"   ·   {self._tokens:,} tok · ${self._cost:.4f}"
        try:
            bar = Text()
            if self._busy:
                elapsed = time.monotonic() - self._t0 if self._t0 else 0.0
                bar.append(self._SPINNER[self._spin] + " ", style=c["accent"])
                bar.append(self._phase, style=c["fg"])
                bar.append(f"   ·   {elapsed:4.1f}s", style=c["dim"])
                bar.append(meter, style=c["dim"])
                bar.append("   ·   esc to stop", style=c["dim"])
            else:
                bar.append(self._phase, style=c["dim"])
                bar.append(meter, style=c["dim"])
            self.query_one("#status", Static).update(bar)
        except Exception:
            pass

    def _banner(self) -> None:
        log = self.query_one("#log", RichLog)
        c = self._col()
        log.write(Text("◆ PRIEST CODE", style=f"bold {c['accent']}"))
        log.write(Text("a fast, transparent terminal coding agent",
                       style=c["dim"]))
        log.write(Text(f"workspace: {self.agent.workspace}", style=c["dim"]))
        log.write(Text("ctrl+p opens the command palette · type /help",
                       style=c["dim"]))
        log.write(Rule(style=c["dim"]))

    def _header_text(self) -> Text:
        c = self._col()
        txt = Text()
        txt.append("◆ PRIEST CODE", style=f"bold {c['accent']}")
        txt.append("   ·   ", style=c["dim"])
        txt.append(self.agent.model.label, style=c["fg"])
        txt.append("   ·   ", style=c["dim"])
        txt.append(f"{Path(self.agent.workspace).name}/", style=c["accent2"])
        txt.append(f"   ·   {self.agent.agent_def.name}", style=c["accent"])
        txt.append(f" · {self.agent.config.approval}", style=c["dim"])
        if self._tokens:
            txt.append(f"   ·   {self._tokens:,} tok · ${self._cost:.4f}",
                       style=c["dim"])
        return txt

    # ── command palette entries (ctrl+p) ─────────────────────────────
    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        yield from super().get_system_commands(screen)
        yield SystemCommand("Model: switch…", "Pick the model to use",
                            self.action_pick_model)
        yield SystemCommand("Model: live free…",
                            "fetch the provider's CURRENT free models and pick one",
                            self.action_pick_live_model)
        for mode, desc in (("diff", "auto-apply edits, confirm shell"),
                           ("confirm", "confirm every write and command"),
                           ("yolo", "auto-approve everything (still blocks "
                            "catastrophic)")):
            yield SystemCommand(f"Approval: {mode}", desc,
                                lambda m=mode: self._set_approval(m))
        from .. import agents as _agents
        pool = _agents.from_config(self.agent.config.agents)
        for name, ad in pool.items():
            ro = " (read-only)" if ad.tools is not None else ""
            yield SystemCommand(f"Agent: {name}", (ad.description + ro).strip(),
                                lambda n=name: self._set_agent(n))
        yield SystemCommand("Undo: last file change",
                            "revert the most recent write or edit",
                            self.action_undo)
        yield SystemCommand("Tasks: toggle panel", "show/hide the task list",
                            self.action_toggle_todo)
        yield SystemCommand("Transcript: clear", "clear the conversation view",
                            self._clear)

    # ── input ────────────────────────────────────────────────────────
    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text or self._busy:
            return
        inp = self.query_one("#prompt", Input)
        inp.value = ""
        if text.startswith("/"):
            self._command(text)
            return
        log = self.query_one("#log", RichLog)
        log.write(Rule(style=self._col()["dim"]))
        log.write(Text(f"❯ {text}", style=f"bold {self._col()['user']}"))
        self._busy = True
        self._streamed = False
        self._prose = ""
        self._t0 = time.monotonic()
        inp.disabled = True
        self._phase = "waiting for the model…"
        self._render_status()
        self._run_agent(text)

    # ── slash commands (a text alias for the palette) ────────────────
    def _command(self, text: str) -> None:
        log = self.query_one("#log", RichLog)
        c = self._col()
        parts = text.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        def line(s, style=None):
            log.write(Text(s, style=style or c["dim"]))

        if cmd in ("/quit", "/exit"):
            self.exit()
        elif cmd in ("/help", "/?"):
            line("commands (or press ctrl+p for the palette):", c["accent"])
            line("  /model [id]     show or switch the model  (ctrl+o)")
            line("  /models         list available models")
            line("  /theme [name]   priest | opencode | mono  (live)")
            line("  /agent [name]   build | plan | <custom>")
            line("  /approval mode  diff | confirm | yolo")
            line("  /undo           revert the last file change  (ctrl+z)")
            line("  @path           attach a file's contents to your message")
            line("  /clear          clear the transcript")
            line("  /quit           exit   ·   esc stops a running turn")
        elif cmd == "/models":
            for pid, prov in P.CATALOG.items():
                line(f"{prov.label} [{pid}]", c["accent2"])
                for m in prov.models:
                    tag = f"  ({m.price_display()})" if m.price else ""
                    line(f"    {m.id}{tag}")
        elif cmd == "/model":
            if not arg:
                self.action_pick_model()
            else:
                self._switch_model(arg)
        elif cmd == "/theme":
            if arg in _theme.BY_NAME:
                self.theme = arg
                self._retint()
                line(f"theme → {arg}", c["ok"])
            else:
                line(f"themes: {', '.join(_theme.names())}", c["dim"])
        elif cmd == "/approval":
            if arg in ("diff", "confirm", "yolo"):
                self._set_approval(arg)
            else:
                line("approval: diff | confirm | yolo", c["dim"])
        elif cmd == "/agent":
            from .. import agents as _agents
            pool = _agents.from_config(self.agent.config.agents)
            if arg in pool:
                self._set_agent(arg)
            else:
                line(f"agents: {', '.join(pool)}", c["dim"])
        elif cmd == "/undo":
            self.action_undo()
        elif cmd == "/clear":
            self._clear()
        else:
            line(f"unknown command {cmd} — try /help or ctrl+p", c["err"])

    # ── model picker ─────────────────────────────────────────────────
    def action_pick_model(self) -> None:
        opts = []
        for pid, prov in P.CATALOG.items():
            for m in prov.models:
                label = Text()
                label.append(f"{m.label}", style="bold")
                if m.price:
                    label.append(f"  {m.price_display()}", style=self._col()["ok"]
                                 if m.price == "free" else self._col()["dim"])
                label.append(f"\n  {m.id}  ·  {prov.label}",
                             style=self._col()["dim"])
                opts.append((f"{pid}||{m.id}", label))

        def picked(result):
            if result:
                pid, mid = result.split("||", 1)
                self._switch_model(mid, pid)
        self.push_screen(PickerModal("Switch model", opts, picked), picked)

    def action_pick_live_model(self) -> None:
        """Fetch the current provider's live FREE models (in a worker, so the UI
        never blocks) and open a picker — so the operator always gets fresh ids
        without touching code when the provider rotates them."""
        self._set_status("fetching live free models…")
        self._fetch_live_free()

    @work(thread=True, exclusive=True, group="livemodels")
    def _fetch_live_free(self) -> None:
        from .. import providers as _P
        try:
            rows = self.agent.client.fetch_model_rows()
            free = _P.live_free_models(self.agent.provider, rows)
        except Exception:
            free = []
        self.call_from_thread(self._show_live_free, free)

    def _show_live_free(self, free) -> None:
        c = self._col()
        if not free:
            self._set_status("no live free models found (network/key?)")
            self.query_one("#log", RichLog).write(Text(
                "  couldn't fetch live free models — check the network/key, or "
                "try `/models`", style=c["warn"]))
            return
        opts = []
        for m in free:
            label = Text()
            label.append(m.label, style="bold")
            label.append("  free", style=c["ok"])
            label.append(f"\n  {m.id}", style=c["dim"])
            opts.append((f"{self.agent.provider.id}||{m.id}", label))

        def picked(result):
            if result:
                pid, mid = result.split("||", 1)
                self._switch_model(mid, pid)
        self._set_status(f"{len(free)} live free models")
        self.push_screen(
            PickerModal(f"Live free models · {self.agent.provider.label}",
                        opts, picked), picked)

    def _switch_model(self, model_id: str, provider_id: str = "") -> None:
        log = self.query_one("#log", RichLog)
        prov = None
        m = None
        if provider_id:
            prov = P.get_provider(provider_id)
            m = prov.model(model_id) if prov else None
        if m is None:
            for pid, pv in P.CATALOG.items():
                mm = pv.model(model_id)
                if mm:
                    prov, m = pv, mm
                    break
        if m is None:
            # allow an arbitrary id on the current provider (live models)
            prov = self.agent.provider
            m = P.Model(model_id, model_id, 128)
        self.agent.provider = prov
        self.agent.model = m
        self.agent.client.provider = prov
        self.agent.config.provider = prov.id
        self.agent.config.model = m.id
        # honour the new provider's tool-calling style (Gemini → text protocol)
        self.agent.native = getattr(prov, "native_tools", True)
        # Switching to a DIFFERENT provider must also repoint the client's
        # endpoint and key, or the new model id gets sent to the old provider's
        # URL with the old key (auth/endpoint failure).
        self.agent.client.base_url = self.agent.config.base_url()
        self.agent.client.api_key = self.agent.config.resolved_key()
        self.query_one("#header", Static).update(self._header_text())
        log.write(Text(f"  model → {m.label}  [{prov.id}]", style=self._col()["ok"]))
        # warn NOW if this provider has no key, instead of failing on the next send
        try:
            if prov.needs_key and not self.agent.config.has_key():
                log.write(Text(f"  ⚠ no API key for {prov.label} — run `priest auth` "
                               f"or set one. {prov.signup}", style=self._col()["warn"]))
        except Exception:
            pass

    def _set_approval(self, mode: str) -> None:
        self.agent.config.approval = mode
        self.query_one("#header", Static).update(self._header_text())
        self.query_one("#log", RichLog).write(
            Text(f"  approval → {mode}", style=self._col()["ok"]))

    def _set_agent(self, name: str) -> None:
        from .. import agents as _agents
        pool = _agents.from_config(self.agent.config.agents)
        ad = pool.get(name)
        if not ad:
            return
        self.agent.set_agent(ad)
        self.query_one("#header", Static).update(self._header_text())
        ro = "  (read-only)" if ad.tools is not None else ""
        self.query_one("#log", RichLog).write(
            Text(f"  agent → {name}{ro}", style=self._col()["ok"]))

    def action_undo(self) -> None:
        c = self._col()
        msg = self.agent.undo()
        self.query_one("#log", RichLog).write(
            Text(f"  ↩ {msg}" if msg else "  nothing to undo",
                 style=c["ok"] if msg else c["dim"]))

    def _clear(self) -> None:
        self.query_one("#log", RichLog).clear()
        self._banner()

    def _retint(self) -> None:
        self.query_one("#header", Static).update(self._header_text())

    # ── agent worker ─────────────────────────────────────────────────
    @work(thread=True, exclusive=True, group="agent")
    def _run_agent(self, text: str) -> None:
        try:
            self.agent.send(text, self._emit, self._approve)
        except Exception as e:  # pragma: no cover
            self._emit(E.Notice(f"internal error: {e}", "error"))
            self._emit(E.Done(0, "error"))

    def _emit(self, ev: E.Event) -> None:
        try:
            self.call_from_thread(self._on_event, ev)
        except Exception:
            pass

    def _approve(self, kind: str, prompt: str, detail: str) -> bool:
        done = threading.Event()
        box = {"ok": False}

        def show():
            def cb(ok):
                box["ok"] = bool(ok)
                done.set()
            self.push_screen(ApproveModal(prompt, detail), cb)
        self.call_from_thread(show)
        done.wait()
        return box["ok"]

    # ── render one event ─────────────────────────────────────────────
    def _on_event(self, ev: E.Event) -> None:
        log = self.query_one("#log", RichLog)
        c = self._col()
        if isinstance(ev, E.AssistantText):
            self._stream_prose(log, c, ev.text)     # show the reply live
        elif isinstance(ev, E.Thinking):
            self._phase = "reasoning…"
        elif isinstance(ev, E.Status):
            self._phase = ev.text
            self._render_status()
        elif isinstance(ev, E.TurnStarted):
            self._phase = "working…"
        elif isinstance(ev, E.TurnFinished):
            self._flush_prose(log, c)
        elif isinstance(ev, E.ToolStarted):
            log.write(Text(f"  → {ev.summary or ev.name}", style=c["accent2"]))
            self._phase = f"{ev.summary or ev.name}…"
        elif isinstance(ev, E.ToolFinished):
            mark, st = ("✓", c["ok"]) if ev.ok else ("✗", c["err"])
            log.write(Text(f"  {mark} {ev.summary or ev.name}", style=st))
            if ev.name == "run" and ev.output:
                log.write(Panel(Text(ev.output[:6000], style=c["fg"]),
                                border_style=c["dim"] if ev.ok else c["err"],
                                title=Text("output", style=c["dim"]),
                                title_align="left", padding=(0, 1)))
        elif isinstance(ev, E.Diff):
            self._write_diff(log, ev, c)
        elif isinstance(ev, E.Notice):
            st = {"error": c["err"], "warn": c["warn"], "ok": c["ok"],
                  "gate": c["accent"]}.get(ev.level, c["dim"])
            log.write(Text(f"  {ev.text}", style=st))
        elif isinstance(ev, E.TodoUpdated):
            self._todos = ev.items
            self._render_todos()
        elif isinstance(ev, E.Usage):
            # keep the running session meter (tokens + $ spent)
            if ev.total_tokens:
                self._tokens = ev.total_tokens
            if ev.total_cost_usd:
                self._cost = ev.total_cost_usd
            self.query_one("#header", Static).update(self._header_text())
            self._render_status()
        elif isinstance(ev, E.Done):
            self._flush_prose(log, c)
            self._busy = False
            inp = self.query_one("#prompt", Input)
            inp.disabled = False
            inp.focus()
            self._phase = {"complete": "ready", "stopped": "stopped",
                           "max_steps": "hit step ceiling",
                           "error": "error"}.get(ev.reason, "ready")
            self._render_status()

    def _stream_prose(self, log: RichLog, c: dict, text: str) -> None:
        """Accumulate the streaming reply and show a live preview of the latest
        words in the status line, so the answer is visibly forming (never frozen).
        The full reply is rendered as markdown when the turn finishes."""
        self._prose += text
        self._streamed = True
        preview = harness.clean_reply(self._prose).replace("\n", " ")
        preview = " ".join(preview.split())
        if preview:
            self._phase = "responding: …" + preview[-72:]
        else:
            self._phase = "responding…"

    def _flush_prose(self, log: RichLog, c: dict) -> None:
        prose = harness.clean_reply(self._prose)
        self._prose = ""
        if prose:
            try:
                log.write(Markdown(prose))
            except Exception:
                log.write(Text(prose, style=c["fg"]))

    def _write_diff(self, log: RichLog, ev: E.Diff, c: dict) -> None:
        head = "created" if ev.created else "edited"
        title = Text()
        title.append(f" {head} ", style=f"bold {c['accent']}")
        title.append(ev.path, style=c["fg"])
        title.append(f"  +{ev.added}", style=c["ok"])
        title.append(f" -{ev.removed} ", style=c["err"])
        if not ev.unified:
            log.write(title)
            return
        body = Text()
        for ln in ev.unified.splitlines()[:400]:
            if ln.startswith(("---", "+++")):
                continue
            if ln.startswith("+"):
                body.append(ln + "\n", style=c["ok"])
            elif ln.startswith("-"):
                body.append(ln + "\n", style=c["err"])
            elif ln.startswith("@@"):
                body.append(ln + "\n", style=c["accent2"])
            else:
                body.append(ln + "\n", style=c["dim"])
        log.write(Panel(body, title=title, title_align="left",
                        border_style=c["dim"], padding=(0, 1)))

    def _render_todos(self) -> None:
        panel = self.query_one("#todo", Static)
        c = self._col()
        if not self._todos:
            panel.remove_class("show")
            return
        panel.add_class("show")
        out = Text()
        out.append("TASKS\n\n", style=f"bold {c['dim']}")
        glyph = {"done": ("✔", c["ok"]), "doing": ("▸", c["accent"]),
                 "todo": ("○", c["dim"])}
        for it in self._todos:
            g, col = glyph.get(it.get("status", "todo"), ("○", c["dim"]))
            out.append(f"{g} ", style=col)
            out.append(f"{it.get('text','')}\n",
                       style=c["dim"] if it.get("status") == "done" else c["fg"])
        panel.update(out)

    def _set_status(self, text: str) -> None:
        self._phase = text
        self._render_status()

    # ── actions ──────────────────────────────────────────────────────
    def action_toggle_todo(self) -> None:
        self.query_one("#todo", Static).toggle_class("show")

    def action_interrupt(self) -> None:
        if self._busy:
            self.agent.stop()
            self._set_status("stopping…")


def run(agent: Agent, theme_name: str = "priest") -> None:
    PriestApp(agent, theme_name).run()
