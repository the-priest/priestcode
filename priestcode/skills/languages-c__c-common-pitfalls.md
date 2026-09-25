---
name: C common pitfalls
description: The sharp edges of C that actually cause bugs — avoid them.
category: languages/c
tags: [c, pitfalls, footguns]
---
# C common pitfalls

## When to use
Writing or reviewing C; catching the language-specific bugs.

## Checklist
- Watch for: Buffer overflows, off-by-one, and unbounded strcpy/sprintf.
- Watch for: Use-after-free, double-free, and leaks — own every malloc.
- Watch for: Undefined behavior (signed overflow, uninit reads) the compiler exploits.
- Watch for: Never use gets(); check every return/length.

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
