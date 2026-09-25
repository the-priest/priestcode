---
name: MySQL
description: Use MySQL correctly for its strengths.
category: databases
tags: [mysql, database]
---
# MySQL

## When to use
Working with MySQL.

## Checklist
- Model data for MySQL's access patterns, not a generic schema.
- Parameterize/validate all input; set resource limits and timeouts.
- Index/shape data for your reads; plan backups and eviction/retention.

## Pitfalls
- Using it as the wrong kind of store for the workload.
- No backups / no eviction policy.
