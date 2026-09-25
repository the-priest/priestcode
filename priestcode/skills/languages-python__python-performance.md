---
name: Python performance
description: Profile and speed up Python code with evidence.
category: languages/python
tags: [python, performance]
---
# Python performance

## When to use
A Python hot path that's too slow — measured, not guessed.

## Checklist
- Profile first: cProfile / py-spy; find the real hot line.
- Fix algorithmics; use built-ins (they're C), sets for membership, local vars in loops.
- Batch I/O; avoid repeated attribute lookups in tight loops.
- Measure before/after.

## Pitfalls
- Micro-optimizing cold code wastes time.
- Premature C-extension before profiling.
