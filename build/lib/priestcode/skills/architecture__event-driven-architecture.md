---
name: Event-driven architecture
description: Design around events and async messaging.
category: architecture
tags: [event-driven, architecture]
---
# Event-driven architecture

## When to use
Deciding on event-driven architecture.

## Checklist
- Model domain events; publish/subscribe with a broker; consumers idempotent.
- Handle ordering, duplicates, and replay; version event schemas.
- Trace flows across async hops.

## Pitfalls
- Hidden coupling via event shapes.
- No idempotency → duplicate side effects.
