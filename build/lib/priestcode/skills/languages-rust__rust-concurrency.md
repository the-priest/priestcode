---
name: Rust concurrency
description: Write correct concurrent/async Rust without races or deadlocks.
category: languages/rust
tags: [rust, concurrency, async]
---
# Rust concurrency

## When to use
Any Rust code doing parallel/async work or shared state.

## Checklist
- Use the language's concurrency model correctly (goroutines/channels, async, threads).
- Protect shared state; prefer message passing; bound parallelism.
- Always handle cancellation/timeouts.

## Pitfalls
- Data races on shared mutable state.
- Unbounded concurrency exhausting resources.
