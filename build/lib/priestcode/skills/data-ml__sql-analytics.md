---
name: SQL analytics
description: Answer analytical questions with SQL correctly.
category: data-ml
tags: [sql, analytics]
---
# SQL analytics

## When to use
Aggregating/reporting from a relational store.

## Checklist
- Use window functions for running/ranked metrics; CTEs for readable steps.
- Mind NULL semantics in aggregates and joins; verify grain (one row per what?).
- Sanity-check totals against a known number.

## Pitfalls
- JOINs that fan out rows inflate SUMs.
- NULLs silently dropped by aggregates/`NOT IN`.
