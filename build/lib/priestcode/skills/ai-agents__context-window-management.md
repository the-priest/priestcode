---
name: Context window management
description: Keep the model's context focused and within budget.
category: ai-agents
tags: [context, llm, ai]
---
# Context window management

## When to use
Building context window management in an LLM app.

## Checklist
- Include only what the task needs; summarize or drop old turns; pin the system prompt.
- Compress bulky tool outputs; track token budget; retrieve on demand rather than stuffing.
- Order matters — put the most relevant last.

## Pitfalls
- Stuffing irrelevant context degrades quality and costs tokens.
- Silently truncating the system prompt.
