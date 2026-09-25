---
name: TypeScript packaging & deps
description: Structure, build, and ship a TypeScript project and its dependencies.
category: languages/typescript
tags: [typescript, packaging, build, dependencies]
---
# TypeScript packaging & deps

## When to use
Setting up, building, or releasing a TypeScript project.

## Checklist
- Use the standard build tool and dependency manager with a lockfile.
- Pin versions; separate runtime vs dev deps; produce reproducible builds.

## Pitfalls
- Unpinned dependencies drift and break builds.
- Committing build artifacts.
