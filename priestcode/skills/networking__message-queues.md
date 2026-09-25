---
name: Message queues
description: Use a queue/broker for reliable async work.
category: networking
tags: [queues, networking]
---
# Message queues

## When to use
Working with message queues.

## Checklist
- At-least-once by default → make consumers idempotent; ack after success.
- Dead-letter poison messages; set visibility timeouts; bound concurrency.
- Order and exactly-once are hard — design around them.

## Pitfalls
- Non-idempotent consumers double-process on redelivery.
- No DLQ → a poison message blocks the queue.
