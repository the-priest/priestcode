---
name: Game state management
description: Manage screens and state cleanly.
category: gamedev
tags: [game-state, gamedev]
---
# Game state management

## When to use
Working on game state management.

## Checklist
- A state/scene stack (menu, play, pause, game-over); clear enter/exit hooks.
- Keep game state separate from rendering; make it serializable for save/load.
- Central update dispatch per state.

## Pitfalls
- Global tangled state across screens.
- Logic and rendering intertwined.
