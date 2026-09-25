---
name: Prompt engineering
description: Get reliable results from an LLM in code.
category: data-ml
tags: [llm, prompting, ai]
---
# Prompt engineering

## When to use
Calling an LLM as part of a program.

## Checklist
- Be specific: role, task, constraints, format; give examples.
- Constrain output (schema/JSON) and validate it; handle failures/retries.
- Keep context focused; test prompts against varied inputs.

## Pitfalls
- Assuming the model follows format without validation.
- Stuffing irrelevant context degrades quality.
