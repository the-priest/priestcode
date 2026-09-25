---
name: Multiplayer netcode
description: Build responsive, cheat-resistant multiplayer.
category: gamedev
tags: [netcode, gamedev]
---
# Multiplayer netcode

## When to use
Working on multiplayer netcode.

## Checklist
- Server-authoritative state; clients send inputs, not positions.
- Client-side prediction + reconciliation; interpolate remote entities.
- Handle latency/loss; never trust the client.

## Pitfalls
- Trusting client-reported state → trivial cheating.
- No interpolation → jittery remote players.
