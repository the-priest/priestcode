---
name: Bash concurrency
description: Write correct concurrent/async Bash without races or deadlocks.
category: languages/bash
tags: [bash, concurrency, async]
---
# Bash concurrency

## When to use
Any Bash code doing parallel/async work or shared state.

## Checklist
- Use the language's concurrency model correctly (goroutines/channels, async, threads).
- Protect shared state; prefer message passing; bound parallelism.
- Always handle cancellation/timeouts.

## Pitfalls
- Data races on shared mutable state.
- Unbounded concurrency exhausting resources.
