---
name: PHP concurrency
description: Write correct concurrent/async PHP without races or deadlocks.
category: languages/php
tags: [php, concurrency, async]
---
# PHP concurrency

## When to use
Any PHP code doing parallel/async work or shared state.

## Checklist
- Use the language's concurrency model correctly (goroutines/channels, async, threads).
- Protect shared state; prefer message passing; bound parallelism.
- Always handle cancellation/timeouts.

## Pitfalls
- Data races on shared mutable state.
- Unbounded concurrency exhausting resources.
