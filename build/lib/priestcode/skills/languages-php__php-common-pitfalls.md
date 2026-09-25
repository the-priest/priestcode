---
name: PHP common pitfalls
description: The sharp edges of PHP that actually cause bugs — avoid them.
category: languages/php
tags: [php, pitfalls, footguns]
---
# PHP common pitfalls

## When to use
Writing or reviewing PHP; catching the language-specific bugs.

## Checklist
- Watch for: Loose comparison `==` type juggling (`'0e1'==’0e2'`); use `===`.
- Watch for: Unsanitized input in SQL/shell/echo (SQLi/XSS/RCE).
- Watch for: `null`/undefined array keys; silent type coercion.
- Watch for: Global state and superglobals.

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
