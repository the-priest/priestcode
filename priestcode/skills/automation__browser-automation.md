---
name: Browser automation
description: Drive a headless browser for tasks/tests.
category: automation
tags: [browser, automation]
---
# Browser automation

## When to use
Working on browser automation.

## Checklist
- Use Playwright/Selenium; wait on conditions not sleeps; stable selectors (roles/test-ids).
- Handle dialogs, downloads, and auth; run headless in CI.
- Clean up contexts; isolate state per run.

## Pitfalls
- Fixed sleeps cause flakiness.
- Leaking browser contexts/processes.
