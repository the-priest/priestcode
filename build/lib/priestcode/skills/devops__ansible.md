---
name: Ansible
description: Use Ansible correctly for reproducible, secure infra/config.
category: devops
tags: [ansible, infra]
---
# Ansible

## When to use
Working with Ansible.

## Checklist
- Keep Ansible config declarative, version-controlled, and reviewed.
- Least privilege; secrets from a manager, never in plaintext config.
- Test changes in a safe environment; make them idempotent/reversible.

## Pitfalls
- Manual drift from the declared state.
- Secrets committed in plaintext.
