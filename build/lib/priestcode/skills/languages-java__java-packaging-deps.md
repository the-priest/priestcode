---
name: Java packaging & deps
description: Structure, build, and ship a Java project and its dependencies.
category: languages/java
tags: [java, packaging, build, dependencies]
---
# Java packaging & deps

## When to use
Setting up, building, or releasing a Java project.

## Checklist
- Use the standard build tool and dependency manager with a lockfile.
- Pin versions; separate runtime vs dev deps; produce reproducible builds.

## Pitfalls
- Unpinned dependencies drift and break builds.
- Committing build artifacts.
