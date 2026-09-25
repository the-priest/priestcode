---
name: GitHub Actions
description: Write secure, efficient GitHub Actions workflows.
category: devops
tags: [github-actions, ci-cd]
---
# GitHub Actions

## When to use
Automating on GitHub.

## Checklist
- Pin actions to a commit SHA; minimal `permissions:`; use OIDC over static secrets.
- Cache dependencies; matrix builds; concurrency to cancel superseded runs.
- Never `pull_request_target` with untrusted checkout + secrets.

## Pitfalls
- `@v3` tags can move; pin SHAs for third-party actions.
- `pull_request_target` + checkout of PR code + secrets = RCE by contributors.
