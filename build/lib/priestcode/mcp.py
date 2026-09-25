"""mcp.py — Model Context Protocol client (local stdio servers).

Priest Code speaks MCP, so any MCP server — GitHub, a database, a docs index,
your own — becomes a set of tools the agent can call, exactly like OpenCode.
Servers are declared in the project config:

    { "mcp": { "servers": {
        "github": { "type": "local",
                    "command": ["npx", "-y", "@github/github-mcp-server"],
                    "environment": { "GITHUB_TOKEN": "..." } } } } }

This implements the stdio transport (newline-delimited JSON-RPC 2.0): spawn the
server, `initialize`, `tools/list`, and `tools/call`. Each remote tool is
wrapped as a native Priest Code Tool (name `mcp__<server>__<tool>`) so it shows
up in the system prompt and the transcript like any other. Best-effort: a
server that fails to start is skipped with a notice, never fatal.
"""

from __future__ import annotations

import json
import os
import subprocess
import threading
from typing import Any, Callable, Dict, List, Optional

from .tools import Tool, ToolContext, ToolResult


class MCPServer:
    def __init__(self, name: str, command: List[str],
                 env: Optional[Dict[str, str]] = None, cwd: Optional[str] = None):
        self.name = name
        self.command = command
        self.env = env or {}
        self.cwd = cwd
        self.proc: Optional[subprocess.Popen] = None
        self._id = 0
        self._lock = threading.Lock()
        self.tools: List[Dict[str, Any]] = []

    def start(self, timeout: float = 30.0) -> None:
        full_env = dict(os.environ)
        full_env.update({k: str(v) for k, v in self.env.items()})
        self.proc = subprocess.Popen(
            self.command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, env=full_env, cwd=self.cwd,
            text=True, bufsize=1)
        self._request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {}, "clientInfo": {"name": "priestcode", "version": "1"},
        }, timeout=timeout)
        self._notify("notifications/initialized", {})
        res = self._request("tools/list", {}, timeout=timeout)
        self.tools = (res or {}).get("tools", []) if isinstance(res, dict) else []

    def call(self, tool: str, arguments: Dict[str, Any],
             timeout: float = 300.0) -> Dict[str, Any]:
        return self._request("tools/call",
                             {"name": tool, "arguments": arguments},
                             timeout=timeout) or {}

    def stop(self) -> None:
        try:
            if self.proc:
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=3)
                except Exception:
                    try:
                        self.proc.kill()
                    except Exception:
                        pass
                for s in (self.proc.stdin, self.proc.stdout):
                    try:
                        s and s.close()
                    except Exception:
                        pass
        except Exception:
            pass

    # ── JSON-RPC over newline-delimited stdio ────────────────────────
    def _next_id(self) -> int:
        self._id += 1
        return self._id

    def _send(self, obj: dict) -> None:
        assert self.proc and self.proc.stdin
        self.proc.stdin.write(json.dumps(obj) + "\n")
        self.proc.stdin.flush()

    def _notify(self, method: str, params: dict) -> None:
        self._send({"jsonrpc": "2.0", "method": method, "params": params})

    def _request(self, method: str, params: dict, timeout: float) -> Any:
        with self._lock:
            rid = self._next_id()
            self._send({"jsonrpc": "2.0", "id": rid, "method": method,
                        "params": params})
            assert self.proc and self.proc.stdout
            # read lines until we see the matching id (skip notifications)
            deadline = threading.Event()

            def _expire():
                # Setting the event is not enough: readline() is blocked and only
                # checked BETWEEN lines, so a server that accepts the request and
                # then goes silent would hang this (agent worker) thread forever.
                # Kill the child so its stdout closes and readline() returns ''.
                deadline.set()
                try:
                    self.proc.kill()
                except Exception:
                    pass
            timer = threading.Timer(timeout, _expire)
            timer.start()
            try:
                while not deadline.is_set():
                    line = self.proc.stdout.readline()
                    if not line:
                        break
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                    except Exception:
                        continue
                    if msg.get("id") == rid:
                        if "error" in msg:
                            raise RuntimeError(msg["error"].get("message", "mcp error"))
                        return msg.get("result")
            finally:
                timer.cancel()
            raise TimeoutError(f"mcp {self.name} {method} timed out")


class MCPTool(Tool):
    """Wraps one remote MCP tool as a Priest Code tool."""

    def __init__(self, server: MCPServer, spec: Dict[str, Any]):
        self._server = server
        self._spec = spec
        self.name = f"mcp__{server.name}__{spec.get('name', 'tool')}"
        desc = spec.get("description", "") or "an MCP tool"
        example = f'<tool name="{self.name}">{{...}}</tool>'
        self.description = f"{example}  // {desc[:120]} (via MCP: {server.name})"

    def summarize(self, args):
        return f"{self.name}"

    def run(self, args, ctx: ToolContext) -> ToolResult:
        try:
            res = self._server.call(self._spec.get("name", ""), args)
        except Exception as e:
            return ToolResult(False, summary="mcp error", output=str(e))
        # flatten MCP content blocks to text
        out = []
        for block in (res.get("content") or []):
            if isinstance(block, dict) and block.get("type") == "text":
                out.append(block.get("text", ""))
        text = "\n".join(out) or json.dumps(res)[:4000]
        is_err = bool(res.get("isError"))
        return ToolResult(not is_err, summary="ok" if not is_err else "error",
                          output=text)


def load_servers(config: Dict[str, Any],
                 notice: Callable[[str], None] = None) -> Dict[str, Tool]:
    """Start every configured MCP server and return {tool_name: MCPTool}."""
    tools: Dict[str, Tool] = {}
    servers = ((config or {}).get("servers")
               or (config or {}).get("mcpServers") or {})
    for name, spec in servers.items():
        if not isinstance(spec, dict) or spec.get("disabled"):
            continue
        if spec.get("type", "local") != "local":
            if notice:
                notice(f"mcp: skipping remote server {name!r} (stdio only)")
            continue
        cmd = spec.get("command")
        if not cmd:
            continue
        srv = MCPServer(name, list(cmd), spec.get("environment", {}))
        try:
            srv.start(timeout=float((spec.get("timeout") or {}).get("startup", 30)
                                    if isinstance(spec.get("timeout"), dict) else 30))
        except Exception as e:
            if notice:
                notice(f"mcp: {name} failed to start ({e})")
            continue
        import atexit
        atexit.register(srv.stop)   # nothing else stops the child otherwise
        for tspec in srv.tools:
            t = MCPTool(srv, tspec)
            tools[t.name] = t
        if notice:
            notice(f"mcp: {name} — {len(srv.tools)} tool(s)")
    return tools
