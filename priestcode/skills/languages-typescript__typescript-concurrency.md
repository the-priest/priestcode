---
name: TypeScript concurrency
description: Write correct concurrent/async TypeScript without races or deadlocks.
category: languages/typescript
tags: [typescript, concurrency, async]
---
# TypeScript concurrency

## When to use
Any TypeScript code doing parallel/async work or shared state.

## Checklist
- Use the language's concurrency model correctly (goroutines/channels, async, threads).
- Protect shared state; prefer message passing; bound parallelism.
- Always handle cancellation/timeouts.

## Pitfalls
- Data races on shared mutable state.
- Unbounded concurrency exhausting resources.
