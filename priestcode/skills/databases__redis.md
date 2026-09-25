---
name: Redis
description: Use Redis correctly for its strengths.
category: databases
tags: [redis, database]
---
# Redis

## When to use
Working with Redis.

## Checklist
- Model data for Redis's access patterns, not a generic schema.
- Parameterize/validate all input; set resource limits and timeouts.
- Index/shape data for your reads; plan backups and eviction/retention.

## Pitfalls
- Using it as the wrong kind of store for the workload.
- No backups / no eviction policy.
