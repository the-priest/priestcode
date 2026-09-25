---
name: LLM evaluation
description: Measure whether an LLM feature actually works.
category: ai-agents
tags: [evals, llm, ai]
---
# LLM evaluation

## When to use
Building llm evaluation in an LLM app.

## Checklist
- Build a labeled eval set of real cases; define pass criteria; run on every change.
- Test edge cases and adversarial inputs; track regressions over time.
- Prefer automatic checks; use human review for the subjective.

## Pitfalls
- Vibe-checking a few prompts and shipping.
- No regression set → silent quality drift.
