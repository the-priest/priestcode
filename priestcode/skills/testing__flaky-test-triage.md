---
name: Flaky test triage
description: Find and fix nondeterministic tests.
category: testing
tags: [flaky, testing]
---
# Flaky test triage

## When to use
Working on flaky test triage.

## Checklist
- Reproduce by re-running/seeding; find the source (time, order, network, concurrency).
- Fix the root cause (fake time/network, isolate state); quarantine only temporarily.
- Track flake rate.

## Pitfalls
- Retrying flakes forever instead of fixing them.
- Ignoring flakes until the suite is untrusted.
