---
name: Ruby concurrency
description: Write correct concurrent/async Ruby without races or deadlocks.
category: languages/ruby
tags: [ruby, concurrency, async]
---
# Ruby concurrency

## When to use
Any Ruby code doing parallel/async work or shared state.

## Checklist
- Use the language's concurrency model correctly (goroutines/channels, async, threads).
- Protect shared state; prefer message passing; bound parallelism.
- Always handle cancellation/timeouts.

## Pitfalls
- Data races on shared mutable state.
- Unbounded concurrency exhausting resources.
