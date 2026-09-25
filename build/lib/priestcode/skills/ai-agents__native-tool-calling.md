---
name: Native tool calling
description: Wire OpenAI-style structured function calling.
category: ai-agents
tags: [tool-calling, llm, ai]
---
# Native tool calling

## When to use
Building native tool calling in an LLM app.

## Checklist
- Send a JSON-schema `tools` array; read structured tool_calls; round-trip role:tool results by id.
- Keep the whole history in one channel (structured) so the model gets no mixed signal.
- Fall back to a text protocol if the provider rejects the tools field.

## Pitfalls
- Mixing structured + text tool history confuses the model.
- Losing the tool_call_id linkage breaks the round-trip.
