---
name: Test fixtures & data
description: Manage test data without coupling tests.
category: testing
tags: [fixtures, testing]
---
# Test fixtures & data

## When to use
Working on test fixtures & data.

## Checklist
- Build fixtures with factories/builders; minimal per-test data; isolate state.
- Deterministic seeds; clean up; avoid shared mutable fixtures.
- Name data by intent.

## Pitfalls
- Giant shared fixtures coupling unrelated tests.
- Order-dependent tests from leaked state.
