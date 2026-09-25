---
name: Secrets in code
description: Find and remediate hardcoded secrets (keys, tokens, passwords).
category: security/appsec
tags: [secrets, gitleaks, appsec]
---
# Secrets in code

## When to use
Code review, pre-commit, or auditing a repo/history for leaked credentials.

## Checklist
- Scan working tree AND full git history (gitleaks, trufflehog) — history keeps deleted secrets.
- Verify hits (many are false positives / test fixtures).
- For real leaks: ROTATE the secret first, then purge from history (BFG/filter-repo).
- FIX: move secrets to env/secret manager; add a pre-commit scanner; add patterns to .gitignore.

## Pitfalls
- Deleting a secret in a new commit does NOT remove it from history — rotate it.
- A public repo leak means assume compromised — rotate immediately.

## Example
gitleaks detect --source . -v
