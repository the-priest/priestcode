---
name: SSRF-to-RCE chains
description: SSRF-to-RCE chains: find, exploit (authorized), and fix.
category: security/web
tags: [ssrf, rce, web]
---
# SSRF-to-RCE chains

## When to use
Escalating an SSRF into code execution.

## Checklist
- From SSRF reach internal admin panels, unauth'd services, or cloud metadata.
- Chain to RCE via an internal vulnerable service or credential theft (authorized).
- FIX: the SSRF fixes (allow-list, IP validation, no redirects) plus internal auth.

## Pitfalls
- Internal services with no auth assume the network is trusted.
- One SSRF + IMDSv1 = cloud account compromise.
