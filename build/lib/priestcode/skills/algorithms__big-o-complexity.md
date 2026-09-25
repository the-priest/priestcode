---
name: Big-O & complexity
description: Reason about time/space complexity.
category: algorithms
tags: [big-o, algorithms]
---
# Big-O & complexity

## When to use
Working on big-o & complexity.

## Checklist
- Identify the dominant term; count nested loops and recursion depth.
- Know the cost of your data-structure ops; pick structures by access pattern.
- Optimize the algorithm before the constant factor.

## Pitfalls
- Hidden O(n) inside a loop (e.g. `in` on a list) → O(n²).
- Optimizing constants while the algorithm is quadratic.
