---
name: Scheduled jobs
description: Run recurring jobs reliably.
category: automation
tags: [cron, automation]
---
# Scheduled jobs

## When to use
Working on scheduled jobs.

## Checklist
- Make jobs idempotent; handle overlap (locking); log start/end/outcome.
- Alert on failure and on missed runs; keep runtimes bounded.
- Store schedules in code/config, not just crontab.

## Pitfalls
- Overlapping runs corrupting shared state.
- Silent failures nobody notices for weeks.
