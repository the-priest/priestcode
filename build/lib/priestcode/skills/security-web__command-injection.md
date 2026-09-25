---
name: Command injection
description: Find and fix OS command injection — input reaching a shell.
category: security/web
tags: [command-injection, rce, shell, owasp]
---
# Command injection

## When to use
Any input passed to a shell: system(), popen(), backticks, exec with shell=True.

## Checklist
- Find sinks: `os.system`, `subprocess(..., shell=True)`, `child_process.exec`, backticks, `Runtime.exec` with a string.
- Probe with shell metacharacters: `; id`, `| id`, `$(id)`, `` `id` ``, newline.
- Blind: time delay (`; sleep 5`) or an OOB DNS/HTTP callback.
- FIX: never build a shell string from input — pass an argv array with NO shell; allow-list where a value must be dynamic.

## Pitfalls
- `shell=True` with any interpolated value is the whole bug; drop the shell.
- Quoting/escaping is fragile — argv arrays are the fix.
- `subprocess.getoutput`/`os.popen` are always shell-backed.

## Example
# safe: subprocess.run(['ping','-c','1', host])  # host still validated
# never: subprocess.run(f'ping -c1 {host}', shell=True)
