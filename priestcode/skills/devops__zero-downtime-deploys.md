---
name: Zero-downtime deploys
description: Deploy without dropping requests.
category: devops
tags: [zero-downtime, devops, sre]
---
# Zero-downtime deploys

## When to use
Working on zero-downtime deploys.

## Checklist
- Rolling/blue-green with health checks; drain connections before stopping old.
- Backward-compatible schema/API changes (expand/contract); readiness gates traffic.
- Automate rollback on failed health.

## Pitfalls
- Breaking schema changes during a rolling deploy.
- No readiness check → traffic to a cold instance.
