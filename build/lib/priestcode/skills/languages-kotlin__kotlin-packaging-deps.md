---
name: Kotlin packaging & deps
description: Structure, build, and ship a Kotlin project and its dependencies.
category: languages/kotlin
tags: [kotlin, packaging, build, dependencies]
---
# Kotlin packaging & deps

## When to use
Setting up, building, or releasing a Kotlin project.

## Checklist
- Use the standard build tool and dependency manager with a lockfile.
- Pin versions; separate runtime vs dev deps; produce reproducible builds.

## Pitfalls
- Unpinned dependencies drift and break builds.
- Committing build artifacts.
