---
name: Feature flags
description: Ship safely behind flags.
category: devops
tags: [feature-flags, devops, sre]
---
# Feature flags

## When to use
Working on feature flags.

## Checklist
- Decouple deploy from release; flag risky changes; target subsets; kill-switch.
- Keep flags short-lived; clean up dead flags; test both states.
- Default safe.

## Pitfalls
- Flag debt: stale flags no one dares remove.
- Untested off-path of a flag.
