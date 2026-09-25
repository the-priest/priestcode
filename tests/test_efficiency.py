#!/usr/bin/env python3
"""test_efficiency.py — the efficiency/big-picture pass: lean prompt, history
compaction, tool-output caps, live free-model discovery, and model self-heal."""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from priestcode import agent as A, config as C, providers as P  # noqa: E402
from priestcode import client as CL, events as E, skills as SK  # noqa: E402

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


print("== the lean skills index is far smaller than the verbose one ==")
sk = SK.load_skills()
lean = SK.skills_index(sk, names=False)
verbose = SK.skills_index(sk, names=True)
ck("lean index is < 1200 chars", len(lean) < 1200, str(len(lean)))
ck("lean is much smaller than verbose", len(lean) * 4 < len(verbose), f"{len(lean)} vs {len(verbose)}")
ck("lean still tells the model to use the skill tool", "skill" in lean)
ck("lean still names the categories", "security" in lean)

print("\n== tool output is capped before it enters history ==")
ws = Path(tempfile.mkdtemp())
ag = A.Agent(C.Config(), P.get_provider("siliconflow"),
             P.get_provider("siliconflow").default_model(), "k", ws)
big = "x" * 100000
capped = ag._cap(big)
ck("a 100k output is capped", len(capped) < 30000, str(len(capped)))
ck("small output is untouched", ag._cap("hello") == "hello")

print("\n== history compaction bounds a long session (and keeps structure) ==")
small_ctx = P.Model("m", "m", 8)          # 8k context → ~8000-token budget
ag2 = A.Agent(C.Config(), P.get_provider("siliconflow"), small_ctx, "k", ws)
# simulate many turns of assistant tool_calls + big tool results
for i in range(40):
    ag2.messages.append({"role": "assistant", "content": None,
                         "tool_calls": [{"id": f"c{i}", "type": "function",
                                         "function": {"name": "read_file",
                                                      "arguments": "{}"}}]})
    ag2.messages.append({"role": "tool", "tool_call_id": f"c{i}",
                         "content": "y" * 3000})
before = ag2._history_tokens()
n_before = len(ag2.messages)
ag2._compact_history(lambda ev: None)
after = ag2._history_tokens()
ck("history was over budget before", before > ag2._ctx_budget(), str(before))
ck("history is within budget after", after <= ag2._ctx_budget(), str(after))
ck("no messages were deleted (tool_call↔tool pairing intact)",
   len(ag2.messages) == n_before, f"{len(ag2.messages)} vs {n_before}")
ck("system prompt preserved", ag2.messages[0]["role"] == "system")
ck("every tool_call still has its matching tool result",
   all(any(m.get("tool_call_id") == tc["id"]
           for m in ag2.messages if m.get("role") == "tool")
       for a in ag2.messages if a.get("tool_calls")
       for tc in a["tool_calls"]))

print("\n== live free-model detection across providers ==")
or_rows = [
    {"id": "vendor/model-a:free", "pricing": {"prompt": "0", "completion": "0"}},
    {"id": "vendor/paid-b", "pricing": {"prompt": "0.5", "completion": "1.0"}},
    {"id": "vendor/model-c", "pricing": {"prompt": "0", "completion": "0"},
     "context_length": 256000},
]
free = P.live_free_models(P.get_provider("openrouter"), or_rows)
ids = {m.id for m in free}
ck("free-by-suffix detected", "vendor/model-a:free" in ids)
ck("free-by-zero-pricing detected", "vendor/model-c" in ids)
ck("paid model excluded", "vendor/paid-b" not in ids)
zen_rows = [{"id": "muse-spark-9.9-contributor-free"}, {"id": "some-paid-model"}]
zfree = {m.id for m in P.live_free_models(P.get_provider("zen"), zen_rows)}
ck("zen -free suffix detected", "muse-spark-9.9-contributor-free" in zfree)
ck("zen non-free excluded", "some-paid-model" not in zfree)

print("\n== a rotated-out model heals itself from the live catalog ==")
ws3 = Path(tempfile.mkdtemp())
ag3 = A.Agent(C.Config(approval="yolo"), P.get_provider("openrouter"),
              P.get_provider("openrouter").default_model(), "k", ws3)
state = {"i": 0}
LIVE_FREE_ID = "vendor/fresh-model:free"


def fake_stream(self, model, messages, on_token, on_reasoning=None, **kw):
    state["i"] += 1
    if model.id != LIVE_FREE_ID:
        # the stale/default id 404s
        return CL.Completion(error="model not found", model_missing=True)
    on_token("healed and answered")
    return CL.Completion(text="healed and answered", finish_reason="stop")


def fake_rows(self, timeout=12.0):
    return [{"id": LIVE_FREE_ID, "pricing": {"prompt": "0", "completion": "0"}}]


_os, _or = CL.Client.stream, CL.Client.fetch_model_rows
CL.Client.stream = fake_stream
CL.Client.fetch_model_rows = fake_rows
try:
    evs = []
    ag3.send("hello", evs.append, lambda k, p, d: True)
finally:
    CL.Client.stream, CL.Client.fetch_model_rows = _os, _or
ck("the agent switched to the live free model", ag3.model.id == LIVE_FREE_ID,
   ag3.model.id)
ck("it recovered and completed (no hard error)",
   any(isinstance(e, E.Done) and e.reason == "complete" for e in evs))
ck("it told the operator it switched",
   any(isinstance(e, E.Notice) and "switched to live free model" in e.text
       for e in evs))

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
