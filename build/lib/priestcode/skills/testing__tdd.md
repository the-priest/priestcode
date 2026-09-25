---
name: TDD
description: Drive design with tests: red-green-refactor.
category: testing
tags: [tdd, testing]
---
# TDD

## When to use
Building new logic where the design is uncertain.

## Checklist
- Write a failing test for the next small behavior (red).
- Make it pass simply (green); then refactor with tests green.
- Repeat in small steps; let tests shape the interface.

## Pitfalls
- Writing tests after defeats the design benefit.
- Big steps make failures hard to localize.
