---
name: Caching strategies
description: Cache to speed things up without serving stale/wrong data.
category: networking
tags: [caching, networking]
---
# Caching strategies

## When to use
Working with caching strategies.

## Checklist
- Pick a pattern (cache-aside, write-through); set TTLs; plan invalidation.
- Key carefully (include what varies); guard against stampedes (locks/jitter).
- Cache only what's safe and hot.

## Pitfalls
- Invalidation bugs serve stale data.
- Caching per-user data under a shared key.
