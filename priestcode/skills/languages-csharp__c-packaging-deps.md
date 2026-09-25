---
name: C# packaging & deps
description: Structure, build, and ship a C# project and its dependencies.
category: languages/csharp
tags: [c, packaging, build, dependencies]
---
# C# packaging & deps

## When to use
Setting up, building, or releasing a C# project.

## Checklist
- Use the standard build tool and dependency manager with a lockfile.
- Pin versions; separate runtime vs dev deps; produce reproducible builds.

## Pitfalls
- Unpinned dependencies drift and break builds.
- Committing build artifacts.
