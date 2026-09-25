---
name: C++ common pitfalls
description: The sharp edges of C++ that actually cause bugs — avoid them.
category: languages/cpp
tags: [c, pitfalls, footguns]
---
# C++ common pitfalls

## When to use
Writing or reviewing C++; catching the language-specific bugs.

## Checklist
- Watch for: Manual memory — prefer RAII/smart pointers over new/delete.
- Watch for: Dangling references/iterators after container reallocation.
- Watch for: Object slicing; the rule of three/five/zero.
- Watch for: UB from data races, signed overflow, invalid casts.

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
