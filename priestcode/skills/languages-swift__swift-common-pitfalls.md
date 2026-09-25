---
name: Swift common pitfalls
description: The sharp edges of Swift that actually cause bugs — avoid them.
category: languages/swift
tags: [swift, pitfalls, footguns]
---
# Swift common pitfalls

## When to use
Writing or reviewing Swift; catching the language-specific bugs.

## Checklist
- Watch for: Force-unwrapping optionals (`!`) crashes on nil.
- Watch for: Retain cycles in closures — use `[weak self]`.
- Watch for: Value vs reference semantics (struct vs class) surprises.
- Watch for: Implicitly unwrapped optionals hiding nils.

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
