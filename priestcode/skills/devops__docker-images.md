---
name: Docker images
description: Write small, secure, reproducible Docker images.
category: devops
tags: [docker, containers]
---
# Docker images

## When to use
Containerizing an app.

## Checklist
- Multi-stage builds; slim/distroless base; pin base tags by digest.
- Run as non-root; copy only what's needed; leverage layer caching (deps before code).
- No secrets in layers or ENV baked into the image; use build args/secrets mounts.
- One process per container; healthcheck.

## Pitfalls
- `latest` base tags break reproducibility.
- Secrets baked into layers persist in history.
- Running as root is an easy container escape amplifier.
