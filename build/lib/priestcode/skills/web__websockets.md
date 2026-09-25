---
name: WebSockets
description: Build real-time features over WebSockets reliably.
category: web
tags: [websockets, web]
---
# WebSockets

## When to use
Working with websockets.

## Checklist
- Authenticate the handshake; validate every message; heartbeat/ping to detect dead peers.
- Handle reconnect with backoff; bound message size and rate.
- Clean up subscriptions on disconnect.

## Pitfalls
- No auth on the socket after upgrade.
- No backpressure → memory blowup.
