---
name: CLI design
description: Design command-line tools people can use.
category: systems
tags: [cli, systems]
---
# CLI design

## When to use
Working with cli design.

## Checklist
- Sensible defaults; --help that teaches; consistent flags; readable + machine output.
- Exit non-zero on failure; errors to stderr; respect pipes and NO_COLOR.
- Confirm destructive actions; support --dry-run.

## Pitfalls
- Exiting 0 on failure breaks scripts.
- Chatty stdout that can't be piped.
