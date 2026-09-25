---
name: Game loop
description: Structure a correct, smooth game loop.
category: gamedev
tags: [game-loop, gamedev]
---
# Game loop

## When to use
Working on game loop.

## Checklist
- Separate update (fixed timestep) from render; use delta time for movement.
- Cap/decouple frame rate; accumulate time for physics stability.
- Handle input, update, render, repeat — keep it deterministic where possible.

## Pitfalls
- Tying movement to frame rate → speed varies by machine.
- Physics in a variable timestep gets unstable.
