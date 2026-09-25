---
name: Swift concurrency
description: Write correct concurrent/async Swift without races or deadlocks.
category: languages/swift
tags: [swift, concurrency, async]
---
# Swift concurrency

## When to use
Any Swift code doing parallel/async work or shared state.

## Checklist
- Use the language's concurrency model correctly (goroutines/channels, async, threads).
- Protect shared state; prefer message passing; bound parallelism.
- Always handle cancellation/timeouts.

## Pitfalls
- Data races on shared mutable state.
- Unbounded concurrency exhausting resources.
