---
name: Log aggregation
description: Centralize logs for search and alerting.
category: devops
tags: [log-aggregation, devops, sre]
---
# Log aggregation

## When to use
Working on log aggregation.

## Checklist
- Ship structured logs off-host to a central store; index by service/request id.
- Retention + PII scrubbing; correlate across services; alert on patterns.
- Keep volume/cost in check with levels/sampling.

## Pitfalls
- Logs only on the host (gone when it dies).
- Logging PII/secrets into the aggregator.
