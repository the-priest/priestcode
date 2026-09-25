---
name: Java common pitfalls
description: The sharp edges of Java that actually cause bugs — avoid them.
category: languages/java
tags: [java, pitfalls, footguns]
---
# Java common pitfalls

## When to use
Writing or reviewing Java; catching the language-specific bugs.

## Checklist
- Watch for: `==` compares references for objects; use `.equals`.
- Watch for: NullPointerException from unchecked nulls; autoboxing NPEs.
- Watch for: Mutable static state and thread-safety bugs.
- Watch for: Catching Exception too broadly hides failures.

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
