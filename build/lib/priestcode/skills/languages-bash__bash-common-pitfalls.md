---
name: Bash common pitfalls
description: The sharp edges of Bash that actually cause bugs — avoid them.
category: languages/bash
tags: [bash, pitfalls, footguns]
---
# Bash common pitfalls

## When to use
Writing or reviewing Bash; catching the language-specific bugs.

## Checklist
- Watch for: Unquoted variables word-split and glob — always quote `"$var"`.
- Watch for: `set -euo pipefail` off by default; errors pass silently.
- Watch for: Parsing `ls`; spaces in filenames breaking loops.
- Watch for: Injection from unquoted input into commands.

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
