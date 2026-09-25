---
name: Configuration & env
description: Manage configuration cleanly across environments.
category: systems
tags: [config, systems]
---
# Configuration & env

## When to use
Working with configuration & env.

## Checklist
- Layer: defaults < file < env < flags; validate on load; fail fast on bad config.
- Secrets from env/manager, not the config file in git.
- Document every setting; sane defaults.

## Pitfalls
- Secrets committed in config files.
- Silent fallback on misconfig hides problems.
