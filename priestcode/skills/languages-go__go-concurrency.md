---
name: Go concurrency
description: Write correct concurrent/async Go without races or deadlocks.
category: languages/go
tags: [go, concurrency, async]
---
# Go concurrency

## When to use
Any Go code doing parallel/async work or shared state.

## Checklist
- Use the language's concurrency model correctly (goroutines/channels, async, threads).
- Protect shared state; prefer message passing; bound parallelism.
- Always handle cancellation/timeouts.

## Pitfalls
- Data races on shared mutable state.
- Unbounded concurrency exhausting resources.
