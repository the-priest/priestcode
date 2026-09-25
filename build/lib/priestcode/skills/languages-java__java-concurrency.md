---
name: Java concurrency
description: Write correct concurrent/async Java without races or deadlocks.
category: languages/java
tags: [java, concurrency, async]
---
# Java concurrency

## When to use
Any Java code doing parallel/async work or shared state.

## Checklist
- Use the language's concurrency model correctly (goroutines/channels, async, threads).
- Protect shared state; prefer message passing; bound parallelism.
- Always handle cancellation/timeouts.

## Pitfalls
- Data races on shared mutable state.
- Unbounded concurrency exhausting resources.
