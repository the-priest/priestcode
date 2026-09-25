---
name: Notifications
description: Deliver notifications without spamming.
category: automation
tags: [notifications, automation]
---
# Notifications

## When to use
Working on notifications.

## Checklist
- Debounce/batch; respect user preferences and quiet hours; make them actionable.
- Handle delivery failures/retries; don't leak sensitive data in them.
- Rate-limit per user.

## Pitfalls
- Alert fatigue from too many low-value pings.
- Leaking secrets/PII in notification bodies.
