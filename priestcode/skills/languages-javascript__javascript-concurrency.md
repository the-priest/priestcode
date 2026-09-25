---
name: JavaScript concurrency
description: Write correct concurrent/async JavaScript without races or deadlocks.
category: languages/javascript
tags: [javascript, concurrency, async]
---
# JavaScript concurrency

## When to use
Any JavaScript code doing parallel/async work or shared state.

## Checklist
- Single-threaded event loop; use async/await; Promise.all for parallel I/O.
- Don't block the loop with sync CPU work — use workers.
- Handle partial failures in Promise.allSettled.

## Pitfalls
- `await` in a loop serializes — batch with Promise.all.
- Blocking the loop freezes the app.
