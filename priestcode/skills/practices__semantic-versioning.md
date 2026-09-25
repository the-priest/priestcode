---
name: Semantic versioning
description: Version releases so consumers know what changed.
category: practices
tags: [semver, releases]
---
# Semantic versioning

## When to use
Publishing a library/API version.

## Checklist
- MAJOR for breaking, MINOR for features, PATCH for fixes.
- Keep a changelog; deprecate before removing; document migrations.
- Don't break on a minor/patch.

## Pitfalls
- Breaking changes in a patch release erode trust.
- 0.x doesn't excuse silent breakage forever.
