---
name: Ruby common pitfalls
description: The sharp edges of Ruby that actually cause bugs — avoid them.
category: languages/ruby
tags: [ruby, pitfalls, footguns]
---
# Ruby common pitfalls

## When to use
Writing or reviewing Ruby; catching the language-specific bugs.

## Checklist
- Watch for: Monkey-patching core classes causes spooky action at a distance.
- Watch for: `nil` errors; truthiness (only nil/false are falsy).
- Watch for: Mutating shared objects passed by reference.
- Watch for: Method-missing magic hiding real errors.

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
