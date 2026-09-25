---
name: SQLite
description: Use SQLite correctly for its strengths.
category: databases
tags: [sqlite, database]
---
# SQLite

## When to use
Working with SQLite.

## Checklist
- Model data for SQLite's access patterns, not a generic schema.
- Parameterize/validate all input; set resource limits and timeouts.
- Index/shape data for your reads; plan backups and eviction/retention.

## Pitfalls
- Using it as the wrong kind of store for the workload.
- No backups / no eviction policy.
