---
name: End-to-end testing
description: Test the full user flow.
category: testing
tags: [e2e, testing, playwright]
---
# End-to-end testing

## When to use
Verifying critical user journeys.

## Checklist
- Cover the few critical paths, not everything (E2E is slow/brittle).
- Use stable selectors (roles/test-ids); wait on conditions, not sleeps.
- Run against a known-seeded environment.

## Pitfalls
- Fixed sleeps and CSS-selector coupling cause flakes.
- E2E-ing everything makes the suite unmaintainable.
