---
name: Kubernetes basics
description: Deploy and operate workloads on Kubernetes safely.
category: devops
tags: [kubernetes, k8s, containers]
---
# Kubernetes basics

## When to use
Deploying to a k8s cluster.

## Checklist
- Set resource requests/limits, liveness/readiness probes.
- Least-privilege: non-root, read-only FS, drop caps, network policies.
- Config in ConfigMaps, secrets in Secrets (or a manager); never in images.
- Use rolling updates with proper readiness to avoid downtime.

## Pitfalls
- No limits → noisy-neighbor and OOM kills.
- Secrets in env/plain manifests leak.
- No readiness probe → traffic to a not-ready pod.
