---
name: Sprite animation
description: Animate sprites smoothly.
category: gamedev
tags: [animation, gamedev]
---
# Sprite animation

## When to use
Working on sprite animation.

## Checklist
- Frame-based animation driven by delta time; sprite sheets; state machines for animations.
- Decouple animation speed from frame rate; loop/hold correctly.
- Pool sprites to avoid churn.

## Pitfalls
- Animation speed tied to frame rate.
- Recreating sprite objects every frame.
