---
name: C# concurrency
description: Write correct concurrent/async C# without races or deadlocks.
category: languages/csharp
tags: [c, concurrency, async]
---
# C# concurrency

## When to use
Any C# code doing parallel/async work or shared state.

## Checklist
- Use the language's concurrency model correctly (goroutines/channels, async, threads).
- Protect shared state; prefer message passing; bound parallelism.
- Always handle cancellation/timeouts.

## Pitfalls
- Data races on shared mutable state.
- Unbounded concurrency exhausting resources.
