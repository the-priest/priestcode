---
name: JavaScript idioms & style
description: Write idiomatic, readable JavaScript the way its community expects.
category: languages/javascript
tags: [javascript, idioms, style]
---
# JavaScript idioms & style

## When to use
Writing or reviewing JavaScript that should look native to the language.

## Checklist
- const by default, let when reassigned, never var; use ===.
- Destructuring, spread, optional chaining, nullish coalescing.
- Array methods (map/filter/reduce) over index loops when clearer.
- Modules (import/export), not globals.

## Pitfalls
- `==` type coercion surprises; use `===`.
- `this` binding in callbacks — use arrow functions.
