---
name: Internationalization
description: Support multiple languages and locales.
category: web
tags: [i18n, web]
---
# Internationalization

## When to use
Working on internationalization.

## Checklist
- Externalize strings; format dates/numbers/currency per locale; handle plurals/RTL.
- Don't concatenate translated fragments; give translators context.
- Test with long strings and RTL.

## Pitfalls
- String concatenation breaks grammar across languages.
- Hardcoded formats/assumptions about text direction.
