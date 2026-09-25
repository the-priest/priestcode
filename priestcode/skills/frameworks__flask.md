---
name: Flask
description: Build small, secure Flask services.
category: frameworks
tags: [flask, python, backend]
---
# Flask

## When to use
Building a Flask app or API.

## Checklist
- Use blueprints; validate input; parameterize DB access.
- Set a strong SECRET_KEY from env; secure session cookies.
- Handle errors with error handlers, not bare try/except everywhere.

## Pitfalls
- Debug mode on in prod exposes the Werkzeug console (RCE).
- Rendering user input in templates → SSTI.
