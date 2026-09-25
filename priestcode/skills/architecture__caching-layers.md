---
name: Caching layers
description: Place caches deliberately across a system.
category: architecture
tags: [cache-layers, architecture]
---
# Caching layers

## When to use
Deciding on caching layers.

## Checklist
- Cache at the right layer (CDN, app, DB) for the access pattern; set TTL + invalidation.
- Avoid stampedes; keep caches consistent with the source of truth.
- Measure hit rate; cache the hot, not everything.

## Pitfalls
- Multiple uncoordinated caches serving conflicting data.
- Caching correctness-critical data without invalidation.
