---
name: Python packaging & deps
description: Structure, build, and ship a Python project and its dependencies.
category: languages/python
tags: [python, packaging, build, dependencies]
---
# Python packaging & deps

## When to use
Setting up, building, or releasing a Python project.

## Checklist
- Use pyproject.toml; a virtualenv or uv/poetry; pin with a lockfile.
- Keep an importable package layout; expose a console entry point.
- Separate runtime vs dev deps.

## Pitfalls
- Committing a venv; unpinned deps that drift.
- `pip install` outside a venv pollutes the system.
