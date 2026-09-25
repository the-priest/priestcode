---
name: Android app security testing
description: Assess an Android APK for common mobile vulnerabilities.
category: security/mobile
tags: [android, mobile, apk, reversing]
---
# Android app security testing

## When to use
Testing an Android app you're authorized to assess.

## Checklist
- Decompile (jadx/apktool); read the manifest for exported components, permissions, debuggable.
- Check for secrets/keys in code and resources; insecure storage (SharedPrefs, SQLite).
- Inspect network: cleartext, cert pinning, and try to bypass pinning (Frida/objection).
- Test exported activities/services/providers for IPC abuse.

## Pitfalls
- `android:exported=true` components are an entry point.
- Client-side secrets are recoverable — treat the app as untrusted.

## Example
jadx-gui app.apk   ;   apktool d app.apk
