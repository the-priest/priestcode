---
name: Profiling workflow
description: Find the real bottleneck before optimizing.
category: performance
tags: [profiling, performance]
---
# Profiling workflow

## When to use
Working on profiling workflow.

## Checklist
- Reproduce a representative workload; profile (CPU/alloc/wall); read the hot path.
- Fix the biggest cost first; re-profile to confirm; stop when good enough.
- Optimize algorithm before constants.

## Pitfalls
- Optimizing by guess/intuition.
- Micro-optimizing cold code.
