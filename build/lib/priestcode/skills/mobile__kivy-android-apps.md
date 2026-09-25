---
name: Kivy Android apps
description: Build single-file Kivy apps that package to Android.
category: mobile
tags: [kivy, android, python]
---
# Kivy Android apps

## When to use
Building a Python mobile app with Kivy.

## Checklist
- Keep the UI in kv or built widgets; keep long work off the UI thread (Clock/threads).
- Request Android permissions at runtime; use plyer/pyjnius for platform APIs.
- Design for touch and small screens; test on device, not just desktop.

## Pitfalls
- Blocking the main thread freezes the UI.
- Assuming desktop behavior matches Android.
