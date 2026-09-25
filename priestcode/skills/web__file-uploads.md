---
name: File uploads
description: Accept file uploads without opening a hole.
category: web
tags: [uploads, web]
---
# File uploads

## When to use
Working with file uploads.

## Checklist
- Validate type by content not extension; cap size; store outside the webroot.
- Randomize stored names; never execute uploads; scan if serving to others.
- Stream large files; set timeouts.

## Pitfalls
- Trusting the extension/MIME from the client.
- Serving uploads from a path that can execute them.
