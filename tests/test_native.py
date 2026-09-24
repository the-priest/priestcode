#!/usr/bin/env python3
"""test_native.py — native (OpenCode-style) function-calling: the client sends a
`tools` schema and reads structured tool_calls; the agent round-trips them as an
assistant.tool_calls message + role:"tool" results and executes for real."""
import json
import os
import sys
import tempfile
import urllib.request
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from priestcode import client as CL, providers as P, tools as T  # noqa: E402
from priestcode import agent as A, config as C  # noqa: E402

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


# ── the tools carry real JSON schemas ────────────────────────────────
print("== tool schemas ==")
tools = T.default_tools()
sch = T.tools_schema(tools)
ck("one schema per tool", len(sch) == len(tools), f"{len(sch)}/{len(tools)}")
wf = next(s for s in sch if s["function"]["name"] == "write_file")
ck("schema is OpenAI function shape", wf["type"] == "function")
ck("write_file requires path+content",
   set(wf["function"]["parameters"]["required"]) == {"path", "content"},
   str(wf["function"]["parameters"]["required"]))
ck("params are typed", wf["function"]["parameters"]["properties"]["path"]["type"] == "string")


# ── the client sends `tools` and returns structured tool_calls ───────
print("\n== client: native request + structured response ==")


class _R:
    def __init__(self, lines):
        self._l = lines

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def __iter__(self):
        return iter(self._l)


def _sse(*objs):
    return [("data: " + json.dumps(o)).encode() for o in objs] + [b"data: [DONE]"]


SENT = {}


def _drive(frames, tools=None, err=None):
    real = urllib.request.urlopen

    def fake(req, timeout=None):
        SENT["body"] = json.loads(req.data.decode())
        if err:
            raise err()
        return _R(frames)
    urllib.request.urlopen = fake
    try:
        prov = P.get_provider("siliconflow")
        c = CL.Client(prov, prov.base_url, "k")
        return c.stream(prov.default_model(), [{"role": "user", "content": "hi"}],
                        on_token=lambda t: None, tools=tools)
    finally:
        urllib.request.urlopen = real


frames = _sse(
    {"choices": [{"delta": {"tool_calls": [
        {"index": 0, "id": "call_abc",
         "function": {"name": "read_file", "arguments": '{"path":'}}]}}]},
    {"choices": [{"delta": {"tool_calls": [
        {"index": 0, "function": {"arguments": ' "app.py"}'}}]}}]},
    {"choices": [{"finish_reason": "tool_calls"}]})
comp = _drive(frames, tools=sch)
ck("request carried a tools array", isinstance(SENT["body"].get("tools"), list)
   and len(SENT["body"]["tools"]) == len(tools))
ck("tool_choice auto sent", SENT["body"].get("tool_choice") == "auto")
ck("enable_thinking:false still sent (DeepSeek)",
   SENT["body"].get("enable_thinking") is False)
ck("structured tool_calls returned", len(comp.tool_calls) == 1, str(comp.tool_calls))
ck("call id preserved", comp.tool_calls[0]["id"] == "call_abc")
ck("call name + args assembled",
   comp.tool_calls[0]["name"] == "read_file"
   and json.loads(comp.tool_calls[0]["arguments"])["path"] == "app.py",
   str(comp.tool_calls[0]))


# ── tools-rejection falls back to the text protocol ──────────────────
print("\n== provider that rejects `tools` degrades cleanly ==")


def _reject():
    import io
    return urllib.error.HTTPError(
        "u", 400, "Bad Request", {},
        io.BytesIO(b'{"error":{"message":"tools field not supported"}}'))


import urllib.error  # noqa: E402
real = urllib.request.urlopen
calls_seen = {"n": 0}


def fake_reject(req, timeout=None):
    calls_seen["n"] += 1
    body = json.loads(req.data.decode())
    if body.get("tools"):
        raise _reject()
    return _R(_sse({"choices": [{"delta": {"content": "hello"}}]}))


urllib.request.urlopen = fake_reject
try:
    prov = P.get_provider("siliconflow")
    comp2 = CL.Client(prov, prov.base_url, "k").stream(
        prov.default_model(), [{"role": "user", "content": "x"}],
        on_token=lambda t: None, tools=sch)
finally:
    urllib.request.urlopen = real
ck("retried without tools", calls_seen["n"] == 2, str(calls_seen))
ck("tools_unsupported flagged", comp2.tools_unsupported is True)
ck("content still came back", comp2.text == "hello", comp2.text)


# ── the AGENT round-trips native calls and executes for real ─────────
print("\n== agent: native round-trip writes a real file ==")
ws = Path(tempfile.mkdtemp())
cfg = C.Config(approval="yolo")
prov = P.get_provider("siliconflow")
ag = A.Agent(cfg, prov, prov.default_model(), "k", ws)

script = [
    # turn 1: a structured write_file call
    CL.Completion(text="", finish_reason="tool_calls", tool_calls=[
        {"id": "c1", "name": "write_file",
         "arguments": json.dumps({"path": "hi.py", "content": "print(1)\n"})}]),
    # turn 2: a plain answer, no calls → ends
    CL.Completion(text="Done — wrote hi.py.", finish_reason="stop"),
]
st = {"i": 0}


def fake_stream(model, messages, on_token, on_reasoning=None, **kw):
    i = st["i"]
    st["i"] += 1
    c = script[min(i, len(script) - 1)]
    if c.text:
        on_token(c.text)
    return c


ag.client.stream = fake_stream
evs = []
ag.send("make hi.py", evs.append, lambda k, p, d: True)

ck("the file was actually written", (ws / "hi.py").is_file())
ck("content correct", (ws / "hi.py").read_text() == "print(1)\n")
# history has the OpenAI shapes
asst = [m for m in ag.messages if m.get("role") == "assistant" and m.get("tool_calls")]
ck("assistant.tool_calls message recorded", len(asst) == 1, str(len(asst)))
ck("tool_call has id+function", asst[0]["tool_calls"][0]["id"] == "c1"
   and asst[0]["tool_calls"][0]["function"]["name"] == "write_file")
toolmsg = [m for m in ag.messages if m.get("role") == "tool"]
ck("role:tool result with matching id",
   len(toolmsg) == 1 and toolmsg[0]["tool_call_id"] == "c1", str(toolmsg))
from priestcode import events as E  # noqa: E402
ck("ended complete", any(isinstance(e, E.Done) and e.reason == "complete"
   for e in evs))

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
