---
name: Mocking & test doubles
description: Use mocks/stubs/fakes correctly.
category: testing
tags: [mocking, testing]
---
# Mocking & test doubles

## When to use
Isolating code from slow/external dependencies.

## Checklist
- Mock at architectural boundaries (network, clock, fs), not internal functions.
- Prefer fakes over deep mock expectations; verify behavior not call minutiae.
- Reset mocks between tests.

## Pitfalls
- Over-mocking tests the mock, not your code.
- Mocking what you own instead of refactoring it.
