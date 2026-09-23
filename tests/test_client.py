#!/usr/bin/env python3
"""test_client.py — the streaming client parses SSE, sends enable_thinking for
DeepSeek, and puts a structured tool call on the TOKEN channel (the Basilisk
bug: a synthesized call must reach the buffer the frontend parses)."""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from priestcode import client as CL  # noqa: E402
from priestcode import providers as P  # noqa: E402
from priestcode import harness as H  # noqa: E402

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


class _R:
    def __init__(self, lines):
        self._lines = lines

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def __iter__(self):
        return iter(self._lines)


SENT = {}


def _sse(*objs):
    return [("data: " + json.dumps(o)).encode() for o in objs] + [b"data: [DONE]"]


def _drive(frames, model):
    toks = []
    real = urllib.request.urlopen

    def fake(req, timeout=None):
        SENT["body"] = json.loads(req.data.decode())
        return _R(frames)

    urllib.request.urlopen = fake
    try:
        prov = P.get_provider("siliconflow")
        c = CL.Client(prov, prov.base_url, "k")
        comp = c.stream(model, [{"role": "user", "content": "x"}],
                        on_token=lambda t: toks.append(t))
    finally:
        urllib.request.urlopen = real
    return "".join(toks), comp


DS = P.get_provider("siliconflow").default_model()   # thinking_off = True

print("== plain content streams through ==")
toks, comp = _drive(_sse({"choices": [{"delta": {"content": "hello "}}],
                          }, {"choices": [{"delta": {"content": "world"}}]}), DS)
ck("content tokens arrive", toks == "hello world", repr(toks))
ck("no error", not comp.error, comp.error)

print("\n== enable_thinking:false is sent for DeepSeek ==")
ck("enable_thinking present and False", SENT["body"].get("enable_thinking") is False,
   str(SENT["body"].get("enable_thinking")))

print("\n== a structured tool call reaches the TOKEN channel ==")
toks, comp = _drive(_sse(
    {"choices": [{"delta": {"reasoning_content": "planning"}}]},
    {"choices": [{"delta": {"tool_calls": [
        {"index": 0, "function": {"name": "write_file",
                                  "arguments": '{"path": "a.py",'}}]}}]},
    {"choices": [{"delta": {"tool_calls": [
        {"index": 0, "function": {"arguments": ' "content": "x"}'}}]}}]},
), DS)
calls = H.parse_tool_calls(toks)     # parse the TOKEN buffer, not comp.text
ck("the call is in the token buffer", len(calls) == 1 and calls[0].name == "write_file",
   repr(toks))
ck("args intact", calls and calls[0].args.get("path") == "a.py", str(calls))

print("\n== a textual call is not doubled by the structured channel ==")
toks, comp = _drive(_sse(
    {"choices": [{"delta": {"content": '<tool name="run">{"command":"ls"}</tool>'}}]},
), DS)
ck("exactly one call", len(H.parse_tool_calls(toks)) == 1, repr(toks))

print("\n== HTTP errors become clean messages, not crashes ==")
import urllib.error  # noqa: E402


def _drive_err(code):
    real = urllib.request.urlopen

    def fake(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, code, "x", {}, None)
    urllib.request.urlopen = fake
    try:
        prov = P.get_provider("siliconflow")
        return CL.Client(prov, prov.base_url, "k").stream(
            DS, [{"role": "user", "content": "x"}], on_token=lambda t: None)
    finally:
        urllib.request.urlopen = real


ck("401 -> auth message", "auth" in _drive_err(401).error.lower())
ck("429 -> rate message", "rate" in _drive_err(429).error.lower())
ck("500 -> transient message", "transient" in _drive_err(500).error.lower())

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
