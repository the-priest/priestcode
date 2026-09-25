---
name: CI/CD pipelines
description: Build reliable, secure CI/CD pipelines.
category: devops
tags: [ci-cd, automation]
---
# CI/CD pipelines

## When to use
Setting up build/test/deploy automation.

## Checklist
- Fast feedback: lint+test on every PR; cache deps; fail fast.
- Pin action/tool versions; least-privilege tokens; scan deps and secrets in CI.
- Separate build from deploy; require green + review before deploy; make deploys reproducible.
- Store artifacts; enable rollback.

## Pitfalls
- Long-lived broad tokens in CI are a breach multiplier.
- Flaky tests that get ignored erode the whole pipeline.
