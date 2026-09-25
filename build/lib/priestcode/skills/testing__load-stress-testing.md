---
name: Load & stress testing
description: Find the capacity and breaking point of a service.
category: testing
tags: [load-testing, performance]
---
# Load & stress testing

## When to use
Before a launch or capacity change.

## Checklist
- Model realistic traffic; ramp up to find the knee and the breaking point.
- Measure p50/p95/p99 latency and error rate under load, not just averages.
- Test from close to prod; watch the whole stack (DB, queues) for the true bottleneck.

## Pitfalls
- Averages hide tail latency — track percentiles.
- Testing the load tool's limits, not the service's.
