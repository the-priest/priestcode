---
name: MCP tool integration
description: Integrate Model Context Protocol tools/servers.
category: ai-agents
tags: [mcp, tools, llm]
---
# MCP tool integration

## When to use
Adding external tools to an agent via MCP.

## Checklist
- Speak JSON-RPC over stdio; handshake, list tools, call by name; map results back.
- Timeout and clean up child processes; handle a hung server (kill to unblock reads).
- Gate tool actions by permission; treat tool output as untrusted data.

## Pitfalls
- Leaking the subprocess/threads when a handshake fails.
- A blocking read with no real timeout hanging the agent.
