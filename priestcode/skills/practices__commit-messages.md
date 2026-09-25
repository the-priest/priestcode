---
name: Commit messages
description: Write commit messages that explain the change.
category: practices
tags: [git, commits]
---
# Commit messages

## When to use
Every commit.

## Checklist
- Imperative subject ≤50 chars; blank line; body explains WHY, not what.
- One logical change per commit; reference issues.
- Make history readable — future debuggers will `git blame` this.

## Pitfalls
- 'fix', 'wip', 'stuff' tell nobody anything.
- Bundling unrelated changes in one commit.
