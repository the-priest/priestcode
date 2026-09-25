---
name: Database migrations
description: Write safe, reversible schema migrations.
category: databases
tags: [migrations, database, schema]
---
# Database migrations

## When to use
Changing a production schema.

## Checklist
- Make migrations reversible; test up AND down.
- For big tables: add columns nullable, backfill in batches, then add constraints — avoid long locks.
- Deploy schema changes backward-compatible with the running code (expand/contract).
- Never edit an applied migration; add a new one.

## Pitfalls
- Adding a NOT NULL column with a default rewrites/locks big tables (DB-dependent).
- Dropping a column the old code still uses breaks during rollout.
