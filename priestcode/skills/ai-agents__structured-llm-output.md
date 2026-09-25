---
name: Structured LLM output
description: Get machine-parseable output from an LLM.
category: ai-agents
tags: [structured-output, llm, ai]
---
# Structured LLM output

## When to use
Building structured llm output in an LLM app.

## Checklist
- Specify a strict schema; use JSON mode/function calling; VALIDATE the output.
- Handle parse failures with a repair prompt or retry; never trust format blindly.
- Give a concrete example of the exact shape.

## Pitfalls
- Assuming valid JSON without validation.
- No repair path when the model drifts from the schema.
