---
name: Choosing data structures
description: Pick the right structure for the job.
category: algorithms
tags: [data-structures, algorithms]
---
# Choosing data structures

## When to use
Working on choosing data structures.

## Checklist
- Set/dict for membership/lookup (O(1)); list for order; heap for top-k/priority.
- Deque for both-ends; tree/sorted for ordered range queries.
- Match the structure to the dominant operation.

## Pitfalls
- Using a list where a set/dict is needed (quadratic lookups).
- Premature exotic structures.
