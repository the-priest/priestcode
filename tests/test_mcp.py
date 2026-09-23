#!/usr/bin/env python3
"""test_mcp.py — the MCP stdio client speaks JSON-RPC to a real subprocess
(a tiny fake MCP server), lists its tools, and calls one."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from priestcode import mcp as MCP  # noqa: E402
from priestcode import tools as T  # noqa: E402

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


# a minimal MCP server: newline-delimited JSON-RPC over stdio
FAKE = r'''
import sys, json
def send(o): sys.stdout.write(json.dumps(o)+"\n"); sys.stdout.flush()
for line in sys.stdin:
    line=line.strip()
    if not line: continue
    msg=json.loads(line)
    m=msg.get("method"); i=msg.get("id")
    if m=="initialize":
        send({"jsonrpc":"2.0","id":i,"result":{"protocolVersion":"2024-11-05","capabilities":{}}})
    elif m=="notifications/initialized":
        pass
    elif m=="tools/list":
        send({"jsonrpc":"2.0","id":i,"result":{"tools":[
            {"name":"echo","description":"echo text back",
             "inputSchema":{"type":"object","properties":{"text":{"type":"string"}}}}]}})
    elif m=="tools/call":
        args=msg["params"]["arguments"]
        send({"jsonrpc":"2.0","id":i,"result":{"content":[{"type":"text","text":"echo: "+args.get("text","")}]}})
    else:
        send({"jsonrpc":"2.0","id":i,"error":{"code":-32601,"message":"no"}})
'''

_dir = Path(tempfile.mkdtemp())
_srv = _dir / "fake_mcp.py"
_srv.write_text(FAKE)

print("== MCP stdio client: start, list, call ==")
cfg = {"servers": {"fake": {"type": "local",
                            "command": [sys.executable, str(_srv)]}}}
tools = MCP.load_servers(cfg, notice=lambda s: None)
ck("a tool was discovered", len(tools) == 1, list(tools))
name = next(iter(tools), "")
ck("tool name is namespaced mcp__fake__echo", name == "mcp__fake__echo", name)

t = tools.get(name)
if t:
    ctx = T.ToolContext(cwd=_dir, approve=lambda *a: True, approval_mode="yolo")
    res = t.run({"text": "hello"}, ctx)
    ck("calling the MCP tool returns its output",
       res.ok and "echo: hello" in res.output, str(res))
    ck("the tool exposes a description for the prompt",
       "MCP: fake" in t.description, t.description[:80])

print("\n== a broken server is skipped, not fatal ==")
bad = {"servers": {"nope": {"type": "local", "command": ["/nonexistent/bin/xyz"]}}}
skipped = MCP.load_servers(bad, notice=lambda s: None)
ck("broken server yields no tools and does not raise", skipped == {})

print("\n== remote servers are skipped (stdio only), cleanly ==")
rem = {"servers": {"r": {"type": "remote", "url": "https://x/mcp"}}}
ck("remote skipped", MCP.load_servers(rem, notice=lambda s: None) == {})

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
