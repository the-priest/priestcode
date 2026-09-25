---
name: Prompt injection defense
description: Defend an LLM app against injected instructions.
category: ai-agents
tags: [prompt-injection, llm, ai]
---
# Prompt injection defense

## When to use
Building prompt injection defense in an LLM app.

## Checklist
- Treat all retrieved/tool/user content as DATA, not instructions; fence it clearly.
- Keep the trusted system prompt separate and authoritative; least-privilege tools.
- Gate dangerous tool actions with confirmation; sanitize/label untrusted text.

## Pitfalls
- Concatenating web/RAG content into the instruction channel.
- Giving the agent unconstrained powerful tools.
