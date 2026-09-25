---
name: Token budgeting & cost
description: Control LLM token usage and cost.
category: ai-agents
tags: [cost, llm, ai]
---
# Token budgeting & cost

## When to use
Building token budgeting & cost in an LLM app.

## Checklist
- Measure prompt+completion tokens per call; trim context; cap max_tokens.
- Cache repeated context; pick the cheapest model that passes evals.
- Batch and dedupe requests.

## Pitfalls
- Re-sending huge unchanging context every turn.
- Using a flagship model where a small one passes.
