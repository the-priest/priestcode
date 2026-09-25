---
name: Integration testing
description: Test components working together.
category: testing
tags: [integration, testing]
---
# Integration testing

## When to use
Verifying units integrate (DB, API, services).

## Checklist
- Test real boundaries (a real test DB, a spun-up service) where it matters.
- Seed and tear down state; isolate tests; use containers/fixtures.
- Assert on observable behavior, not internals.

## Pitfalls
- Shared mutable test DB causes order-dependent flakiness.
- Mocking the very boundary you're trying to verify.
