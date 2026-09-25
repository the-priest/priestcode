---
name: Monitoring & alerting
description: Instrument a service so you know when it breaks.
category: devops
tags: [monitoring, observability, sre]
---
# Monitoring & alerting

## When to use
Operating a service in production.

## Checklist
- Emit the four golden signals: latency, traffic, errors, saturation.
- Alert on symptoms users feel (SLO burn), not every blip; make alerts actionable.
- Dashboards for triage; structured logs correlated by request id.

## Pitfalls
- Alert fatigue from noisy, non-actionable alerts.
- Logging without correlation ids makes tracing impossible.
