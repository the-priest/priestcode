#!/usr/bin/env python3
"""test_feed.py — the live activity feed (Status events) and the cost meter."""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from priestcode import providers as P, agent as A, config as C  # noqa: E402
from priestcode import client as CL, events as E                # noqa: E402

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


print("== pricing: V4.1-Flash and V4-Flash are NOT the same price ==")
sf = P.get_provider("siliconflow")
v41 = sf.model("deepseek-ai/DeepSeek-V4.1-Flash")
v4 = sf.model("deepseek-ai/DeepSeek-V4-Flash")
ck("V4.1 and V4 prices differ", v41.price != v4.price,
   f"{v41.price} vs {v4.price}")
ck("V4.1 is 0.30/1.20", v41.rates() == (0.3, 1.2), str(v41.rates()))
ck("V4 is 0.13/0.28", v4.rates() == (0.13, 0.28), str(v4.rates()))

print("\n== cost math ==")
ck("cost = in*rate_in + out*rate_out per 1M",
   abs(v41.cost_usd(1_000_000, 0) - 0.30) < 1e-9
   and abs(v41.cost_usd(0, 1_000_000) - 1.20) < 1e-9)
ck("free model costs nothing",
   P.get_provider("zen").model("muse-spark-1.3-contributor-free").cost_usd(9e9, 9e9) == 0.0)

print("\n== the agent emits a live feed (Status) and a cost meter (Usage) ==")
ws = Path(tempfile.mkdtemp())
cfg = C.Config(approval="yolo")
prov = P.get_provider("siliconflow")
ag = A.Agent(cfg, prov, v41, "k", ws)

script = [
    CL.Completion(text="", finish_reason="tool_calls",
                  prompt_tokens=1000, completion_tokens=200, tool_calls=[
                      {"id": "s1", "name": "skill",
                       "arguments": json.dumps({"action": "load",
                                                "name": "SQL injection"})}]),
    CL.Completion(text="All done.", finish_reason="stop",
                  prompt_tokens=1500, completion_tokens=50),
]
st = {"i": 0}


def fake_stream(self, model, messages, on_token, on_reasoning=None, **kw):
    i = st["i"]; st["i"] += 1
    c = script[min(i, len(script) - 1)]
    if c.text:
        on_token(c.text)
    return c


_orig = CL.Client.stream
CL.Client.stream = fake_stream
try:
    evs = []
    ag.send("look up sql injection then finish", evs.append, lambda k, p, d: True)
finally:
    CL.Client.stream = _orig

statuses = [e for e in evs if isinstance(e, E.Status)]
phases = {e.phase for e in statuses}
ck("Status events were emitted", bool(statuses), str(len(statuses)))
ck("a 'skill' status shows the skill loading", "skill" in phases, str(phases))
ck("a 'responding' status shows the reply forming", "responding" in phases, str(phases))

usages = [e for e in evs if isinstance(e, E.Usage)]
ck("Usage events carry a running token total",
   any(u.total_tokens > 0 for u in usages))
ck("Usage events carry a running $ cost",
   any(u.total_cost_usd > 0 for u in usages))
# expected total cost: (1000+1500) in * 0.30/1M + (200+50) out * 1.20/1M
expected = (2500 * 0.30 + 250 * 1.20) / 1_000_000
ck("session cost meter is correct",
   abs(ag.spent_usd - expected) < 1e-9, f"{ag.spent_usd} vs {expected}")
ck("token meter is correct", ag.prompt_tokens_total == 2500
   and ag.completion_tokens_total == 250)

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
