---
name: API integration
description: Integrate a third-party API robustly.
category: automation
tags: [api-integration, automation]
---
# API integration

## When to use
Working on api integration.

## Checklist
- Read the docs and rate limits; auth securely; handle pagination and partial data.
- Timeouts, retries with backoff, and idempotency; validate responses.
- Wrap it behind a small client you can test/mock.

## Pitfalls
- No timeout/retry → your app inherits their outages.
- Trusting response shapes without validation.
