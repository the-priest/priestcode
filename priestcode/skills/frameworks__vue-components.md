---
name: Vue components
description: Build Vue 3 components with the Composition API correctly.
category: frameworks
tags: [vue, frontend]
---
# Vue components

## When to use
Building or fixing a Vue app.

## Checklist
- Use `<script setup>` + composition API; ref/reactive appropriately.
- Computed for derived state; watchers only for side effects.
- Props down, events up; avoid mutating props.

## Pitfalls
- Losing reactivity by destructuring reactive objects.
- Mutating props instead of emitting.
