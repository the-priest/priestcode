---
name: TypeScript common pitfalls
description: The sharp edges of TypeScript that actually cause bugs — avoid them.
category: languages/typescript
tags: [typescript, pitfalls, footguns]
---
# TypeScript common pitfalls

## When to use
Writing or reviewing TypeScript; catching the language-specific bugs.

## Checklist
- Watch for: `any` and `as` casts silently disable the type checker.
- Watch for: Types are erased at runtime — validate external data.
- Watch for: Structural typing lets unexpected shapes through.
- Watch for: Non-null `!` assertions hide real nulls.

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
