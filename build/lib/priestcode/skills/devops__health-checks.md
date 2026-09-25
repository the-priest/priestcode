---
name: Health checks
description: Expose liveness/readiness correctly.
category: devops
tags: [health-checks, devops, sre]
---
# Health checks

## When to use
Working on health checks.

## Checklist
- Liveness = am I alive (restart if not); readiness = can I serve (gate traffic).
- Check real dependencies in readiness, not liveness; keep them cheap.
- Fail readiness during startup/shutdown.

## Pitfalls
- Liveness that checks deps causes restart storms.
- Readiness always-true → traffic to a broken instance.
