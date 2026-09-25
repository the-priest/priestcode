---
name: Unit testing
description: Write focused, fast unit tests.
category: testing
tags: [unit, testing]
---
# Unit testing

## When to use
Testing a single unit of logic.

## Checklist
- One behavior per test; arrange-act-assert; descriptive names.
- Cover happy path, edges, and error paths; deterministic, no I/O.
- Add a failing test first when fixing a bug (it should fail, then pass).

## Pitfalls
- Testing implementation details makes refactors painful.
- Hidden shared state between tests.
