---
name: Python testing
description: Write and run effective Python tests with the standard tooling.
category: languages/python
tags: [python, testing]
---
# Python testing

## When to use
Adding or fixing tests in a Python project.

## Checklist
- pytest with plain asserts; fixtures for setup; parametrize edge cases.
- Test the happy path, edges, and error paths; add a regression test per bug.
- Mock at boundaries (monkeypatch), not internals.
- Run: `python -m pytest -q`.

## Pitfalls
- Over-mocking tests the mock, not the code.
- Shared mutable fixtures leak state between tests.
