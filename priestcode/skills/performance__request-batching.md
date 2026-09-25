---
name: Request batching
description: Reduce round-trips by batching.
category: performance
tags: [batching, performance]
---
# Request batching

## When to use
Working on request batching.

## Checklist
- Batch N small calls into one (dataloader pattern); debounce bursts.
- Bound batch size and latency; handle partial failures.
- Cache within a request.

## Pitfalls
- Batching that adds unacceptable latency.
- One failure failing the whole batch when it needn't.
