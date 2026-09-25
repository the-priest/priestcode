---
name: PostgreSQL
description: Use Postgres well — schema, queries, and features.
category: databases
tags: [postgres, sql, database]
---
# PostgreSQL

## When to use
Designing or querying a Postgres DB.

## Checklist
- Right types (jsonb, arrays, timestamptz); constraints enforce invariants.
- Parameterized queries only; use EXPLAIN ANALYZE to tune.
- Index for your query patterns; partial/expression indexes when apt.
- Transactions with the right isolation level.

## Pitfalls
- Missing indexes on FK/filter columns cause seq scans.
- Storing timestamps without timezone.
- SELECT * in hot paths.
