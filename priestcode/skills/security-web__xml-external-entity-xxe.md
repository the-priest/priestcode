---
name: XML external entity (XXE)
description: Find and fix XXE — XML parsers resolving external entities.
category: security/web
tags: [xxe, xml, ssrf, owasp]
---
# XML external entity (XXE)

## When to use
Any endpoint parsing user-supplied XML (SOAP, SVG, DOCX/XLSX, config uploads).

## Checklist
- Inject a DOCTYPE with an external entity reading `file:///etc/passwd` or an OOB URL.
- Try parameter entities for blind/OOB exfiltration.
- FIX: disable DTDs and external entities in the parser (defusedxml in Python).

## Pitfalls
- Almost every default XML parser is vulnerable unless explicitly hardened.
- SVG and Office files are XML — file uploads are an XXE surface.

## Example
# python: use defusedxml, or set resolve_entities=False / disable DTD
