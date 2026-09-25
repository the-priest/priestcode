---
name: Progressive web apps
description: Make a web app installable and offline-capable.
category: web
tags: [pwa, web]
---
# Progressive web apps

## When to use
Working on progressive web apps.

## Checklist
- Add a manifest + service worker; cache the shell; handle offline gracefully.
- Update strategy for the SW; HTTPS required; test install/offline.
- Don't cache what must be fresh.

## Pitfalls
- Aggressive SW caching serving stale app forever.
- No update path for a deployed service worker.
