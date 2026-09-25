---
name: JavaScript testing
description: Write and run effective JavaScript tests with the standard tooling.
category: languages/javascript
tags: [javascript, testing]
---
# JavaScript testing

## When to use
Adding or fixing tests in a JavaScript project.

## Checklist
- Jest/Vitest; describe/it; test async with await; mock modules at the boundary.
- Cover edges and error paths; snapshot only stable output.
- Run: `npm test`.

## Pitfalls
- Flaky tests from real timers/network — fake them.
- Snapshot everything → brittle tests.
