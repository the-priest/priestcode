---
name: HTTP caching
description: Use HTTP caching correctly for speed and correctness.
category: web
tags: [caching, web]
---
# HTTP caching

## When to use
Working with http caching.

## Checklist
- Set Cache-Control/ETag/Last-Modified deliberately; validate with conditional requests.
- Cache static assets hard (immutable + hashed names); be careful with authenticated responses.
- Bust caches with versioned URLs.

## Pitfalls
- Caching private/authed responses in shared caches.
- No cache busting → stale assets.
