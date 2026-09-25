---
name: Git workflow
description: Work effectively with git day to day.
category: practices
tags: [git, vcs]
---
# Git workflow

## When to use
Any project under git.

## Checklist
- Small, focused commits with clear messages; branch per change; rebase/merge per team norms.
- Pull/rebase before pushing; review diffs before committing (`git diff --staged`).
- Keep main green; use PRs for review.

## Pitfalls
- Giant mixed commits are unreviewable and unrevertable.
- Committing secrets or generated files.
