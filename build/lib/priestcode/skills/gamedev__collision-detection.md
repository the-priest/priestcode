---
name: Collision detection
description: Detect collisions correctly and cheaply.
category: gamedev
tags: [collision, gamedev]
---
# Collision detection

## When to use
Working on collision detection.

## Checklist
- Broad phase (grid/quadtree) then narrow phase (AABB/circle/SAT).
- Use swept tests for fast objects to avoid tunneling.
- Resolve overlaps stably.

## Pitfalls
- Checking every pair (O(n²)) without a broad phase.
- Tunneling: fast objects passing through thin walls.
