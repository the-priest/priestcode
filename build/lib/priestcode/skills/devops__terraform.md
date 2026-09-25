---
name: Terraform
description: Use Terraform correctly for reproducible, secure infra/config.
category: devops
tags: [terraform, infra]
---
# Terraform

## When to use
Working with Terraform.

## Checklist
- Keep Terraform config declarative, version-controlled, and reviewed.
- Least privilege; secrets from a manager, never in plaintext config.
- Test changes in a safe environment; make them idempotent/reversible.

## Pitfalls
- Manual drift from the declared state.
- Secrets committed in plaintext.
