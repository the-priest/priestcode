---
name: MongoDB
description: Use MongoDB correctly for its strengths.
category: databases
tags: [mongodb, database]
---
# MongoDB

## When to use
Working with MongoDB.

## Checklist
- Model data for MongoDB's access patterns, not a generic schema.
- Parameterize/validate all input; set resource limits and timeouts.
- Index/shape data for your reads; plan backups and eviction/retention.

## Pitfalls
- Using it as the wrong kind of store for the workload.
- No backups / no eviction policy.
