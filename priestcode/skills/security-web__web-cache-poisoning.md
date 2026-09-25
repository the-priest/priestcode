---
name: Web cache poisoning
description: Web cache poisoning: find, exploit (authorized), and fix.
category: security/web
tags: [cache-poisoning, web]
---
# Web cache poisoning

## When to use
Getting a harmful response cached and served to others.

## Checklist
- Find unkeyed inputs (headers) that affect the response but aren't in the cache key.
- Poison via that input; confirm it's served to others.
- FIX: include all response-affecting inputs in the cache key; sanitize.

## Pitfalls
- Reflecting unkeyed headers into cached responses.
- Overly aggressive caching of dynamic content.
