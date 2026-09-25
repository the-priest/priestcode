---
name: Server-side template injection (SSTI)
description: Find and exploit/fix SSTI — user input evaluated by a template engine, leading to RCE.
category: security/web
tags: [ssti, rce, template, owasp]
---
# Server-side template injection (SSTI)

## When to use
User input concatenated into a template string (Jinja2, Twig, Freemarker, ERB, Velocity).

## Checklist
- Probe with `{{7*7}}`, `${7*7}`, `<%= 7*7 %>` — a `49` means evaluation.
- Fingerprint the engine, then reach the sandbox escape / object graph to RCE.
- FIX: never build templates from input — pass input as DATA to a fixed template; sandbox if truly needed.

## Pitfalls
- Rendering user-controlled template SOURCE is the bug; user DATA in a fixed template is fine.
- Jinja2 autoescape protects against XSS, not SSTI.

## Example
# vuln: Template('Hi ' + name).render()
# safe: Template('Hi {{name}}').render(name=name)
