---
name: Swift packaging & deps
description: Structure, build, and ship a Swift project and its dependencies.
category: languages/swift
tags: [swift, packaging, build, dependencies]
---
# Swift packaging & deps

## When to use
Setting up, building, or releasing a Swift project.

## Checklist
- Use the standard build tool and dependency manager with a lockfile.
- Pin versions; separate runtime vs dev deps; produce reproducible builds.

## Pitfalls
- Unpinned dependencies drift and break builds.
- Committing build artifacts.
