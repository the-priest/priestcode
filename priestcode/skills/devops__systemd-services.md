---
name: systemd services
description: Use systemd services correctly for reproducible, secure infra/config.
category: devops
tags: [systemd, infra]
---
# systemd services

## When to use
Working with systemd services.

## Checklist
- Keep systemd services config declarative, version-controlled, and reviewed.
- Least privilege; secrets from a manager, never in plaintext config.
- Test changes in a safe environment; make them idempotent/reversible.

## Pitfalls
- Manual drift from the declared state.
- Secrets committed in plaintext.
