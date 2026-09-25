---
name: Go packaging & deps
description: Structure, build, and ship a Go project and its dependencies.
category: languages/go
tags: [go, packaging, build, dependencies]
---
# Go packaging & deps

## When to use
Setting up, building, or releasing a Go project.

## Checklist
- Use the standard build tool and dependency manager with a lockfile.
- Pin versions; separate runtime vs dev deps; produce reproducible builds.

## Pitfalls
- Unpinned dependencies drift and break builds.
- Committing build artifacts.
