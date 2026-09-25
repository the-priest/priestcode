---
name: Buildozer packaging
description: Package a Python app to an APK with Buildozer.
category: mobile
tags: [buildozer, android, packaging]
---
# Buildozer packaging

## When to use
Turning a Kivy/Python app into an installable APK.

## Checklist
- Declare requirements, permissions, and API levels in buildozer.spec.
- Match python-for-android recipes for native deps; clean builds when deps change.
- Test the release APK on a real device; sign it for distribution.

## Pitfalls
- Missing a requirement/permission → runtime crash on device.
- Debug vs release signing confusion.
