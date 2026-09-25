---
name: Connection pooling
description: Reuse expensive connections correctly.
category: performance
tags: [pooling, performance]
---
# Connection pooling

## When to use
Working on connection pooling.

## Checklist
- Pool DB/HTTP connections; size the pool to the workload and limits.
- Set acquire timeouts; validate/health-check idle conns; close on shutdown.
- Avoid leaks — always return connections.

## Pitfalls
- Leaked connections exhausting the pool.
- Oversized pools overwhelming the DB.
