---
name: Cloud metadata & SSRF
description: Cloud metadata & SSRF: find, exploit (authorized), and fix.
category: security/cloud
tags: [cloud, ssrf, metadata]
---
# Cloud metadata & SSRF

## When to use
SSRF against cloud metadata endpoints.

## Checklist
- From an SSRF, hit 169.254.169.254 for instance credentials/role tokens.
- Use the creds to enumerate cloud permissions (authorized).
- FIX: enforce IMDSv2, block metadata from app egress, scope IAM roles tightly.

## Pitfalls
- IMDSv1 hands out creds to any SSRF.
- Over-broad instance roles turn one SSRF into full account access.
