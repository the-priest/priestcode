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


print("== pricing: V4.1-Flash has off-peak AND peak rates (not always peak) ==")
import datetime  # noqa: E402
sf = P.get_provider("siliconflow")
v41 = sf.model("deepseek-ai/DeepSeek-V4.1-Flash")
v4 = sf.model("deepseek-ai/DeepSeek-V4-Flash")
# a known off-peak moment (Sunday) and a known peak moment (Tue 02:00 UTC)
offpeak = datetime.datetime(2026, 9, 27, 2, 0, tzinfo=datetime.timezone.utc)  # Sun
peak = datetime.datetime(2026, 9, 29, 2, 0, tzinfo=datetime.timezone.utc)     # Tue 02:00
ck("V4.1 off-peak rate is 0.15/0.60", v41.rates(offpeak) == (0.15, 0.60),
   str(v41.rates(offpeak)))
ck("V4.1 peak rate is 0.30/1.20", v41.rates(peak) == (0.30, 1.20),
   str(v41.rates(peak)))
ck("V4.1 is NOT charged the peak rate off-peak",
   v41.cost_usd(1_000_000, 0, offpeak) < v41.cost_usd(1_000_000, 0, peak))
ck("V4 has a single flat rate (0.13/0.28) regardless of hour",
   v4.rates(offpeak) == v4.rates(peak) == (0.13, 0.28))
ck("peak window: Tue 02:00 UTC is peak, Sun 02:00 is not",
   P.is_peak(peak) and not P.is_peak(offpeak))

print("\n== cost math ==")
ck("off-peak cost = in*0.15 + out*0.60 per 1M",
   abs(v41.cost_usd(1_000_000, 0, offpeak) - 0.15) < 1e-9
   and abs(v41.cost_usd(0, 1_000_000, offpeak) - 0.60) < 1e-9)
ck("free model costs nothing",
   P.get_provider("zen").model("muse-spark-1.3-contributor-free").cost_usd(9e9, 9e9) == 0.0)

print("\n== free-tier resilience: a provider that rejects params still works ==")
import io           # noqa: E402
import urllib.error  # noqa: E402
import urllib.request  # noqa: E402


def _sse(*chunks):
    lines = [("data: " + json.dumps(o)).encode() for o in chunks] + [b"data: [DONE]"]

    class _R:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def __iter__(self): return iter(lines)
    return _R()


calls = {"n": 0, "bodies": []}


def fake_urlopen(req, timeout=None):
    calls["n"] += 1
    body = json.loads(req.data.decode())
    calls["bodies"].append(body)
    # a free endpoint that 400s on ANY of the provider-specific extensions,
    # with a GENERIC message that names nothing (the hard case)
    if any(k in body for k in ("tools", "enable_thinking", "reasoning_effort",
                               "tool_choice")):
        raise urllib.error.HTTPError(
            "u", 400, "Bad Request", {},
            io.BytesIO(b'{"error":{"message":"invalid request body"}}'))
    return _sse({"choices": [{"delta": {"content": "hello from free tier"}}]})


_real = urllib.request.urlopen
urllib.request.urlopen = fake_urlopen
try:
    prov_or = P.get_provider("openrouter")
    c = CL.Client(prov_or, prov_or.base_url, "k")
    comp = c.stream(prov_or.default_model(),
                    [{"role": "user", "content": "hi"}],
                    on_token=lambda t: None,
                    tools=[{"type": "function",
                            "function": {"name": "x", "parameters": {}}}])
finally:
    urllib.request.urlopen = _real
ck("degraded and returned content (did not hard-fail)",
   comp.text == "hello from free tier", repr(comp.text) + f" err={comp.error!r}")
ck("it retried after stripping the rejected params", calls["n"] >= 2, str(calls["n"]))
ck("the final request carried none of the rejected extensions",
   all(k not in calls["bodies"][-1] for k in
       ("tools", "enable_thinking", "reasoning_effort", "tool_choice")))
ck("tools_unsupported was flagged for the caller's fallback",
   comp.tools_unsupported is True)

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
# total spend = the model's own (time-aware) cost for 2500 in + 250 out
expected = v41.cost_usd(2500, 250)
ck("session cost meter matches the model's rate (time-aware)",
   abs(ag.spent_usd - expected) < 1e-6, f"{ag.spent_usd} vs {expected}")
ck("session cost is > 0", ag.spent_usd > 0)
ck("token meter is correct", ag.prompt_tokens_total == 2500
   and ag.completion_tokens_total == 250)

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
