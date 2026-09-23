#!/usr/bin/env python3
"""test_tui.py — the full-screen app mounts, renders a scripted coding session
end-to-end without crashing, and slash commands work. Headless via Textual's
own test pilot (no real terminal)."""
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from priestcode import agent as A, client as CL, config as C, providers as P  # noqa

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


def _tool(n, a):
    return f'<tool name="{n}">{json.dumps(a)}</tool>'


SCRIPT = [
    "I'll write it.\n" + _tool("write_file",
                               {"path": "x.py", "content": "print(1)\n", "mode": "create"}),
    "Done — wrote x.py.",
]


async def main():
    from priestcode.tui.app import PriestApp, ApproveModal
    from textual.widgets import Input, RichLog, Static

    ws = Path(tempfile.mkdtemp())
    cfg = C.Config(approval="yolo", theme="priest")
    prov = P.get_provider("siliconflow")
    ag = A.Agent(cfg, prov, prov.default_model(), "k", ws)
    st = {"i": 0}

    def fake(model, messages, on_token, on_reasoning=None, **kw):
        i = st["i"]
        st["i"] += 1
        txt = SCRIPT[min(i, len(SCRIPT) - 1)]
        on_token(txt)
        return CL.Completion(text=txt, finish_reason="stop")
    ag.client.stream = fake

    app = PriestApp(ag, "priest")
    async with app.run_test(size=(110, 30)) as pilot:
        await pilot.pause()
        ck("widgets mounted", all(app.query(sel) for sel in
           ("#log", "#prompt", "#header", "#status")))

        # run a scripted coding session
        inp = app.query_one("#prompt", Input)
        inp.value = "make x.py"
        app.on_input_submitted(Input.Submitted(inp, inp.value))
        for _ in range(60):
            await pilot.pause(0.05)
            if not app._busy:
                break
        ck("session completed (not stuck busy)", not app._busy)
        ck("the file was really written", (ws / "x.py").is_file())

        # slash commands don't crash
        for c in ("/help", "/models", "/model", "/theme opencode", "/clear"):
            inp.value = c
            app.on_input_submitted(Input.Submitted(inp, c))
            await pilot.pause()
        ck("slash commands ran without error", True)

        # /model switches the active model
        inp.value = "/model zai-org/GLM-5.3-Flash"
        app.on_input_submitted(Input.Submitted(inp, inp.value))
        await pilot.pause()
        ck("/model switched the model",
           app.agent.model.id == "zai-org/GLM-5.3-Flash", app.agent.model.id)

        # /agent plan switches to read-only mode (write tool disappears)
        inp.value = "/agent plan"
        app.on_input_submitted(Input.Submitted(inp, inp.value))
        await pilot.pause()
        ck("/agent switched to plan (read-only)",
           app.agent.agent_def.name == "plan"
           and "write_file" not in app.agent.tools, list(app.agent.tools))
        inp.value = "/agent build"
        app.on_input_submitted(Input.Submitted(inp, inp.value))
        await pilot.pause()
        ck("/agent build restores the write tool",
           "write_file" in app.agent.tools)

        # /undo doesn't crash with nothing to undo
        inp.value = "/undo"
        app.on_input_submitted(Input.Submitted(inp, inp.value))
        await pilot.pause()
        ck("/undo is safe with an empty stack", True)

        # approval modal builds
        app.push_screen(ApproveModal("Run this?", "ls -la"))
        await pilot.pause()
        ck("approval modal opened", isinstance(app.screen, ApproveModal))
        app.screen.dismiss(True)
        await pilot.pause()

    ck("all three themes build CSS",
       all(PriestApp(ag, th).CSS for th in ("priest", "opencode", "mono")))


asyncio.run(main())
print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
