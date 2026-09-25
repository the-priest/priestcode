---
name: JavaScript common pitfalls
description: The sharp edges of JavaScript that actually cause bugs — avoid them.
category: languages/javascript
tags: [javascript, pitfalls, footguns]
---
# JavaScript common pitfalls

## When to use
Writing or reviewing JavaScript; catching the language-specific bugs.

## Checklist
- Watch for: `==` coercion; always use `===`.
- Watch for: `this` rebinds in callbacks — use arrows or bind.
- Watch for: Floating-point money math; `0.1+0.2 !== 0.3`.
- Watch for: `typeof null === 'object'`; array holes; `[]+[]`.

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
