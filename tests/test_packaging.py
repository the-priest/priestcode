#!/usr/bin/env python3
"""test_packaging.py — the repo is shippable: metadata is consistent, no key
file is committable, and the README's screenshots exist."""
import os
import re
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


def path(*a):
    return os.path.join(_ROOT, *a)


print("== metadata ==")
pyproject = open(path("pyproject.toml")).read()
from priestcode import __version__  # noqa: E402
ck("pyproject version matches package",
   f'version = "{__version__}"' in pyproject, __version__)
ck("entry point 'priest' declared", 'priest = "priestcode.cli:main"' in pyproject)
ck("textual + rich are dependencies",
   "textual" in pyproject and "rich" in pyproject)
ck("both packages listed", "priestcode.tui" in pyproject)

print("\n== the API-key guard ==")
gi = open(path(".gitignore")).read()
ck(".gitignore excludes config.json (keys)", "config.json" in gi)
ck(".gitignore excludes __pycache__", "__pycache__" in gi)
ck("no config.json committed in the repo",
   not os.path.exists(path("config.json")))

print("\n== required files ==")
for f in ("README.md", "LICENSE", "install.sh", "pyproject.toml"):
    ck(f"{f} present", os.path.isfile(path(f)))
ck("LICENSE is MIT", "MIT License" in open(path("LICENSE")).read())

print("\n== README screenshots exist ==")
readme = open(path("README.md")).read()
for m in re.findall(r'src="(assets/[^"]+)"', readme):
    ck(f"{m} exists", os.path.isfile(path(m)), m)
ck("install one-liner present in README",
   "raw.githubusercontent.com/the-priest/priestcode" in readme)

print("\n== install.sh sanity ==")
sh = open(path("install.sh")).read()
ck("install.sh has a bash shebang", sh.startswith("#!/usr/bin/env bash"))
ck("install.sh sets up a venv (PEP 668 safe)", "venv" in sh)
ck("install.sh points at the repo", "the-priest/priestcode" in sh)

print("\n== every module imports ==")
import importlib  # noqa: E402
for mod in ("cli", "agent", "client", "tools", "harness", "safety", "config",
            "providers", "context", "permissions", "agents", "snapshots",
            "mcp", "session", "render", "prompts", "events", "tui.app",
            "tui.theme"):
    try:
        importlib.import_module(f"priestcode.{mod}")
        ck(f"import priestcode.{mod}", True)
    except Exception as e:
        ck(f"import priestcode.{mod}", False, str(e))

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
