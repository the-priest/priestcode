---
name: Secrets management
description: Handle secrets safely across dev and prod.
category: devops
tags: [secrets, security, devops]
---
# Secrets management

## When to use
Any secret (keys, tokens, DB creds).

## Checklist
- Store in a secret manager / env, never in code or images.
- Least-privilege scoping; rotate regularly and on suspected exposure.
- Separate secrets per environment; audit access.

## Pitfalls
- Secrets in git history persist after deletion — rotate.
- One shared god-credential everywhere.
