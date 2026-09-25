---
name: Rate limiting
description: Protect endpoints with correct rate limiting.
category: web
tags: [rate-limiting, web]
---
# Rate limiting

## When to use
Working with rate limiting.

## Checklist
- Choose a key (user/IP/API-key) and algorithm (token bucket/sliding window).
- Return 429 with Retry-After; limit per-endpoint by cost.
- Enforce server-side, distributed if multi-instance.

## Pitfalls
- Per-instance limits don't hold behind a load balancer.
- Limiting by IP only punishes shared NATs.
