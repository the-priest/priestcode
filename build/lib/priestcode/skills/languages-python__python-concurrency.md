---
name: Python concurrency
description: Write correct concurrent/async Python without races or deadlocks.
category: languages/python
tags: [python, concurrency, async]
---
# Python concurrency

## When to use
Any Python code doing parallel/async work or shared state.

## Checklist
- I/O-bound: asyncio or threads. CPU-bound: multiprocessing (the GIL blocks threads).
- asyncio: never call blocking code in a coroutine; use `to_thread`.
- Guard shared state with locks; prefer queues over shared mutables.
- Always await/cancel tasks; handle CancelledError.

## Pitfalls
- Blocking the event loop freezes everything.
- Threads won't speed up CPU work under the GIL.
