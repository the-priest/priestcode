---
name: Rust common pitfalls
description: The sharp edges of Rust that actually cause bugs — avoid them.
category: languages/rust
tags: [rust, pitfalls, footguns]
---
# Rust common pitfalls

## When to use
Writing or reviewing Rust; catching the language-specific bugs.

## Checklist
- Watch for: Fighting the borrow checker instead of restructuring ownership.
- Watch for: `.unwrap()`/`.expect()` panic in production paths.
- Watch for: Integer overflow panics in debug, wraps in release.
- Watch for: Holding a lock across an `.await` can deadlock.

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
