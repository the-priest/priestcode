---
name: Refactoring safely
description: Improve code structure without changing behavior.
category: practices
tags: [refactoring, maintainability]
---
# Refactoring safely

## When to use
Code that's hard to change but works.

## Checklist
- Get tests green first; make small behavior-preserving steps; re-run tests each step.
- Rename for clarity, remove duplication, split big units, tighten interfaces.
- Never mix a refactor with a feature/bugfix in one commit.

## Pitfalls
- Refactoring without tests is just rewriting and hoping.
- Big-bang rewrites lose behavior and history.
