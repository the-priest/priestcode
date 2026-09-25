---
name: C testing
description: Write and run effective C tests with the standard tooling.
category: languages/c
tags: [c, testing]
---
# C testing

## When to use
Adding or fixing tests in a C project.

## Checklist
- Use the standard test framework and runner.
- Cover the happy path, edges, and error paths; regression-test each bug.
- Keep tests fast, isolated, and deterministic.

## Pitfalls
- Non-deterministic tests erode trust.
- Testing implementation details instead of behavior.
