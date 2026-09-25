---
name: SQL indexing
description: Add the right indexes to make queries fast.
category: databases
tags: [sql, indexing, performance, database]
---
# SQL indexing

## When to use
A slow query or a table that will grow.

## Checklist
- Read the query plan; find the seq scan / sort / nested loop hurting you.
- Index columns used in WHERE/JOIN/ORDER BY; composite index column order matters (equality then range).
- Covering indexes to avoid table lookups; partial indexes for skewed data.
- Re-check the plan after adding — confirm it's used.

## Pitfalls
- Too many indexes slow writes and waste space.
- Wrong composite order = index unused.
- Functions on indexed columns disable the index.
