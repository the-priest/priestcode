#!/usr/bin/env python3
"""test_agent.py — the loop, end to end, with a mocked model: a degraded
DeepSeek native call gets parsed, the tool runs for real, results feed back,
and a tool-free reply ends the turn (no loop)."""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from priestcode import agent as A, client as CL, config as C, providers as P  # noqa
from priestcode import events as E  # noqa: E402

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


FW = "｜"
SEP = "▁"


def ds(name, body):   # a DEGRADED native call (ascii pipe, underscore sep)
    p, s = "|", "_"
    return (f"<{p}tool{s}call{s}begin{p}>function<{p}tool{s}sep{p}>{name}\n"
            f"```json\n{body}\n```<{p}tool{s}call{s}end{p}>")


def run(script, approval="yolo", approve=None):
    ws = Path(tempfile.mkdtemp())
    cfg = C.Config(approval=approval)
    prov = P.get_provider("siliconflow")
    ag = A.Agent(cfg, prov, prov.default_model(), "k", ws)
    state = {"i": 0}

    def fake_stream(model, messages, on_token, on_reasoning=None, **kw):
        i = state["i"]
        state["i"] += 1
        txt = script[min(i, len(script) - 1)]
        on_token(txt)
        return CL.Completion(text=txt, finish_reason="stop")
    ag.client.stream = fake_stream
    evs = []
    ag.send("do it", evs.append, approve or (lambda k, p, d: True))
    return ws, evs


print("== a degraded native write_file call runs, then the turn ends ==")
ws, evs = run([
    "Building it.\n" + ds("write_file",
                          '{"path": "hi.py", "content": "print(1)\\n", "mode": "create"}'),
    "Done — wrote hi.py.",
])
ck("file was actually written", (ws / "hi.py").is_file())
ck("content correct", (ws / "hi.py").read_text() == "print(1)\n")
ck("a Diff event was emitted", any(isinstance(e, E.Diff) for e in evs))
ck("a Done event ended it", any(isinstance(e, E.Done) for e in evs))
done = [e for e in evs if isinstance(e, E.Done)][-1]
ck("ended 'complete' (not max_steps)", done.reason == "complete", done.reason)

print("\n== a tool-free reply ends immediately ==")
ws, evs = run(["Just answering, no tools needed."])
ck("one Done, reason complete",
   [e for e in evs if isinstance(e, E.Done)][0].reason == "complete")
ck("no tool events", not any(isinstance(e, E.ToolStarted) for e in evs))

print("\n== run tool respects a declining approver ==")
ws, evs = run([ds("run", '{"command": "touch SHOULD_NOT_EXIST"}'),
               "ok, skipped."],
              approval="confirm", approve=lambda k, p, d: False)
ck("declined command did not run", not (ws / "SHOULD_NOT_EXIST").exists())

print("\n== catastrophic command is refused even before approval ==")
ws, evs = run([ds("run", '{"command": "rm -rf /"}'), "won't do that."],
              approval="yolo")
tf = [e for e in evs if isinstance(e, E.ToolFinished) and e.name == "run"]
ck("run refused", tf and not tf[0].ok, str(tf))

print("\n== an unknown tool is reported, not crashed ==")
ws, evs = run([ds("frobnicate", "{}"), "never mind."])
ck("unknown tool -> ToolFinished not ok",
   any(isinstance(e, E.ToolFinished) and not e.ok for e in evs))
ck("still reached Done", any(isinstance(e, E.Done) for e in evs))

print("\n== max_steps ceiling holds if the model never stops ==")
ws, evs = run([ds("read_file", '{"path": "hi.py"}')] * 2)   # always a tool call
# script clamps to the last (a tool call), so it would loop → ceiling
cfg_done = [e for e in evs if isinstance(e, E.Done)][-1]
ck("hit the ceiling, bounded", cfg_done.reason == "max_steps", cfg_done.reason)

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
