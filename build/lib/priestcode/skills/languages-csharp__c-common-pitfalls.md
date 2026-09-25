---
name: C# common pitfalls
description: The sharp edges of C# that actually cause bugs — avoid them.
category: languages/csharp
tags: [c, pitfalls, footguns]
---
# C# common pitfalls

## When to use
Writing or reviewing C#; catching the language-specific bugs.

## Checklist
- Watch for: `==` on reference types vs `.Equals`; nullable reference warnings.
- Watch for: async void (except handlers) swallows exceptions.
- Watch for: Disposing IDisposable — use `using`.
- Watch for: Blocking on async (`.Result`/`.Wait`) can deadlock.

## Pitfalls
- These are the bugs that pass review and bite in production.
- When one looks intentional, leave a comment saying why.
