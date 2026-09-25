---
name: Retries & backoff
description: Retry transient failures without making things worse.
category: networking
tags: [retries, networking]
---
# Retries & backoff

## When to use
Working with retries & backoff.

## Checklist
- Only retry idempotent/transient failures; exponential backoff WITH jitter; cap attempts.
- Respect Retry-After; add a circuit breaker for a failing dependency.
- Make the operation idempotent (idempotency keys).

## Pitfalls
- Synchronized retries cause a thundering herd.
- Retrying a 400/auth error forever.
