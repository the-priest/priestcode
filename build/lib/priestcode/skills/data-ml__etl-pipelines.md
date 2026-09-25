---
name: ETL pipelines
description: Build reliable, reproducible data pipelines.
category: data-ml
tags: [etl, data-engineering]
---
# ETL pipelines

## When to use
Moving/transforming data between systems.

## Checklist
- Make steps idempotent and re-runnable; checkpoint; validate at each stage.
- Handle late/duplicate/partial data; log row counts and rejects.
- Separate extract, transform, load; keep transforms testable.

## Pitfalls
- Non-idempotent loads double data on retry.
- No validation → garbage propagates downstream.
