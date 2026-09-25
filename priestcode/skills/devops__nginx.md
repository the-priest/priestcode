---
name: nginx
description: Use nginx correctly for reproducible, secure infra/config.
category: devops
tags: [nginx, infra]
---
# nginx

## When to use
Working with nginx.

## Checklist
- Keep nginx config declarative, version-controlled, and reviewed.
- Least privilege; secrets from a manager, never in plaintext config.
- Test changes in a safe environment; make them idempotent/reversible.

## Pitfalls
- Manual drift from the declared state.
- Secrets committed in plaintext.
