---
name: Preventing N+1 queries
description: Find and kill N+1 query patterns.
category: databases
tags: [performance, orm, database]
---
# Preventing N+1 queries

## When to use
An endpoint issuing many small queries.

## Checklist
- Log/inspect query count per request; find the loop issuing per-row queries.
- Batch with a join / IN clause / eager loading (select_related, includes).
- Cache read-heavy lookups when correct to do so.

## Pitfalls
- ORMs hide N+1 behind lazy attributes.
- Eager-loading everything over-fetches — load what you use.
