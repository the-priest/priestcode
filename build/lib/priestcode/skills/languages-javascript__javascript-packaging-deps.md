---
name: JavaScript packaging & deps
description: Structure, build, and ship a JavaScript project and its dependencies.
category: languages/javascript
tags: [javascript, packaging, build, dependencies]
---
# JavaScript packaging & deps

## When to use
Setting up, building, or releasing a JavaScript project.

## Checklist
- package.json scripts; a lockfile; ESM modules; a bundler if shipping to browsers.
- Separate dependencies vs devDependencies; pin versions.

## Pitfalls
- Committing node_modules; unpinned ranges that break builds.
- Mixing ESM/CJS carelessly.
