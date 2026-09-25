---
name: Bash performance
description: Profile and speed up Bash code with evidence.
category: languages/bash
tags: [bash, performance]
---
# Bash performance

## When to use
A Bash hot path that's too slow — measured, not guessed.

## Checklist
- Measure with a profiler before optimizing.
- Fix the algorithm before micro-optimizing; reduce allocations in hot paths.
- Prove the speedup with before/after numbers.

## Pitfalls
- Guessing the bottleneck.
- Trading correctness/clarity for a micro-gain.
