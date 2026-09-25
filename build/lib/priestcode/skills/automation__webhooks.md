---
name: Webhooks
description: Send and receive webhooks safely.
category: automation
tags: [webhooks, automation]
---
# Webhooks

## When to use
Working on webhooks.

## Checklist
- Verify signatures on inbound; respond fast then process async; dedupe by event id.
- Retry outbound with backoff; make handlers idempotent.
- Validate payloads; guard against SSRF on any URL you call.

## Pitfalls
- Not verifying signatures → spoofed events.
- Slow synchronous handlers timing out the sender.
