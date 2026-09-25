---
name: Ruby performance
description: Profile and speed up Ruby code with evidence.
category: languages/ruby
tags: [ruby, performance]
---
# Ruby performance

## When to use
A Ruby hot path that's too slow — measured, not guessed.

## Checklist
- Measure with a profiler before optimizing.
- Fix the algorithm before micro-optimizing; reduce allocations in hot paths.
- Prove the speedup with before/after numbers.

## Pitfalls
- Guessing the bottleneck.
- Trading correctness/clarity for a micro-gain.
