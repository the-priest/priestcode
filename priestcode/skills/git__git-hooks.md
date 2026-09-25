---
name: git hooks
description: Automate checks with git hooks.
category: git
tags: [hooks, git, vcs]
---
# git hooks

## When to use
Using git hooks.

## Checklist
- pre-commit for lint/format/secret-scan; commit-msg for message rules.
- Keep hooks fast; share them (pre-commit framework) so the team gets them.
- Server-side hooks for enforced policy.

## Pitfalls
- Slow hooks make people `--no-verify`.
- Local-only hooks not shared with the team.
