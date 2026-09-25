---
name: Python idioms & style
description: Write idiomatic, readable Python the way its community expects.
category: languages/python
tags: [python, idioms, style]
---
# Python idioms & style

## When to use
Writing or reviewing Python that should look native to the language.

## Checklist
- Prefer comprehensions, generators, and unpacking over manual loops where clearer.
- Use dataclasses/NamedTuple for records; context managers for resources.
- EAFP over LBYL; iterate directly, use enumerate/zip.
- Type-hint public functions; run mypy/pyright.

## Pitfalls
- Mutable default args (`def f(x=[])`) share state across calls.
- `is` vs `==`; `is` only for None/singletons.
