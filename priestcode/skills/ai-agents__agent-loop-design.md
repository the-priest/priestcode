---
name: Agent loop design
description: Structure a reliable model→tools→observe loop.
category: ai-agents
tags: [agent-loop, llm, ai]
---
# Agent loop design

## When to use
Building agent loop design in an LLM app.

## Checklist
- Stream the model, parse tool calls, execute, feed results back, repeat until done.
- Bound the loop (max steps); detect and break empty/degraded replies.
- Keep the system prompt authoritative; make tools return actionable errors.

## Pitfalls
- No step ceiling → runaway loops.
- Silent empty replies stalling the loop without a retry/backstop.
