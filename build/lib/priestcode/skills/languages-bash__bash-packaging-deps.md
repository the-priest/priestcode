---
name: Bash packaging & deps
description: Structure, build, and ship a Bash project and its dependencies.
category: languages/bash
tags: [bash, packaging, build, dependencies]
---
# Bash packaging & deps

## When to use
Setting up, building, or releasing a Bash project.

## Checklist
- Use the standard build tool and dependency manager with a lockfile.
- Pin versions; separate runtime vs dev deps; produce reproducible builds.

## Pitfalls
- Unpinned dependencies drift and break builds.
- Committing build artifacts.
