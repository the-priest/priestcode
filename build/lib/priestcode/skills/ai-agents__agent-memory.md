---
name: Agent memory
description: Give an agent durable, relevant memory.
category: ai-agents
tags: [memory, llm, ai]
---
# Agent memory

## When to use
Building agent memory in an LLM app.

## Checklist
- Separate short-term (conversation) from long-term (facts, retrieved on need).
- Store durable facts, not transient chatter; dedupe; retrieve by relevance.
- Bound the memory scan; keep it correct and private.

## Pitfalls
- Remembering everything → noise and privacy risk.
- Full-scan recall that grows unbounded per turn.
