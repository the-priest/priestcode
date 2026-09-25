---
name: Kotlin concurrency
description: Write correct concurrent/async Kotlin without races or deadlocks.
category: languages/kotlin
tags: [kotlin, concurrency, async]
---
# Kotlin concurrency

## When to use
Any Kotlin code doing parallel/async work or shared state.

## Checklist
- Use the language's concurrency model correctly (goroutines/channels, async, threads).
- Protect shared state; prefer message passing; bound parallelism.
- Always handle cancellation/timeouts.

## Pitfalls
- Data races on shared mutable state.
- Unbounded concurrency exhausting resources.
