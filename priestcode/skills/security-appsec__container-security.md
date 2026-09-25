---
name: Container security
description: Container security: find, exploit (authorized), and fix.
category: security/appsec
tags: [containers, docker, security]
---
# Container security

## When to use
Hardening a containerized workload.

## Checklist
- Minimal base, non-root, read-only FS, dropped caps, no privileged mode.
- Scan images for CVEs; keep secrets out of layers; sign/verify images.
- Least-privilege at runtime (seccomp/apparmor); network policies.

## Pitfalls
- Root + privileged containers = easy host compromise.
- Secrets baked into image layers.
