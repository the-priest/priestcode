---
name: Data cleaning
description: Turn messy data into trustworthy data.
category: data-ml
tags: [data-cleaning, etl]
---
# Data cleaning

## When to use
Raw data before analysis or loading.

## Checklist
- Profile first: nulls, dupes, types, ranges, outliers.
- Handle each deliberately (impute/drop/flag); document decisions.
- Validate against a schema; keep the raw copy; make cleaning reproducible.

## Pitfalls
- Silent coercion (dates/numbers) corrupts data.
- Dropping rows without understanding why they're bad.
