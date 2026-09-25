---
name: Android intents
description: Use Android intents to integrate with other apps.
category: mobile
tags: [android, intents]
---
# Android intents

## When to use
Launching another app/activity or sharing data.

## Checklist
- Build explicit intents for a known target, implicit for an action; set data/extras/MIME.
- Verify a handler exists before launching; handle the no-handler case.
- Least-privilege on exported components you expose.

## Pitfalls
- Assuming a target app is installed.
- Exporting components that leak IPC.
