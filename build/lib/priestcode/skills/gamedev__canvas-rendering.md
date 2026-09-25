---
name: Canvas rendering
description: Render efficiently on HTML5 canvas.
category: gamedev
tags: [canvas, gamedev]
---
# Canvas rendering

## When to use
Working on canvas rendering.

## Checklist
- Batch draws; minimize state changes; only redraw what changed when possible.
- Use requestAnimationFrame; offscreen canvas for static layers; sprite atlases.
- Clear/compose deliberately.

## Pitfalls
- Redrawing everything every frame when little changed.
- Per-frame allocations causing GC stutter.
