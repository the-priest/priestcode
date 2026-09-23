#!/usr/bin/env python3
"""test_tools.py — every tool behaves, writes stay inside the workspace, edits
produce diffs, create mode works, and run is gated + safe."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from priestcode import tools as T  # noqa: E402

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


ws = Path(tempfile.mkdtemp(prefix="pc_tools_"))
approvals = {"answer": True}
ctx = T.ToolContext(cwd=ws, approve=lambda k, p, d: approvals["answer"],
                    approval_mode="confirm")
tools = T.default_tools()

print("== write_file: create (the persona's default mode) ==")
r = tools["write_file"].run({"path": "game.html", "content": "<h1>hi</h1>",
                             "mode": "create"}, ctx)
ck("create returns ok", r.ok, str(r))
ck("file exists", (ws / "game.html").is_file())
ck("diff shows creation", r.diff and r.diff["created"] and r.diff["added"] == 1)

print("\n== write_file: nested create makes parent dirs ==")
r = tools["write_file"].run({"path": "a/b/c.txt", "content": "x"}, ctx)
ck("nested create ok", r.ok and (ws / "a/b/c.txt").is_file(), str(r))

print("\n== write_file: append ==")
tools["write_file"].run({"path": "log.txt", "content": "one\n"}, ctx)
r = tools["write_file"].run({"path": "log.txt", "content": "two\n",
                            "mode": "append"}, ctx)
ck("append adds", (ws / "log.txt").read_text() == "one\ntwo\n", str(r))

print("\n== path escape is refused ==")
r = tools["write_file"].run({"path": "../escape.txt", "content": "x"}, ctx)
ck("escape refused", not r.ok, str(r))
ck("no file outside ws", not (ws.parent / "escape.txt").exists())

print("\n== read_file ==")
r = tools["read_file"].run({"path": "game.html"}, ctx)
ck("read ok + numbered", r.ok and "1│<h1>hi</h1>" in r.output, r.output)
r = tools["read_file"].run({"path": "nope.txt"}, ctx)
ck("missing file -> not ok", not r.ok)

print("\n== edit_file exact find/replace ==")
tools["write_file"].run({"path": "app.py", "content": "def foo():\n    pass\n"}, ctx)
r = tools["edit_file"].run({"path": "app.py", "old": "def foo():",
                           "new": "def foo(x):"}, ctx)
ck("edit ok", r.ok and "def foo(x):" in (ws / "app.py").read_text(), str(r))
ck("edit has diff", r.diff and r.diff["added"] >= 1)
r = tools["edit_file"].run({"path": "app.py", "old": "nonexistent", "new": "y"}, ctx)
ck("no-match edit refused", not r.ok)

print("\n== list_dir / tree / glob / grep ==")
ck("list_dir ok", tools["list_dir"].run({"path": "."}, ctx).ok)
ck("tree ok", "game.html" in tools["tree"].run({"path": "."}, ctx).output)
ck("glob finds py", "app.py" in tools["glob"].run({"pattern": "**/*.py"}, ctx).output)
gr = tools["grep"].run({"pattern": "def foo", "glob": "**/*.py"}, ctx)
ck("grep finds match", gr.ok and "app.py" in gr.output, gr.output)

print("\n== run: gated + catastrophic-refused ==")
approvals["answer"] = True
r = tools["run"].run({"command": "echo hello"}, ctx)
ck("approved run works", r.ok and "hello" in r.output, str(r))
approvals["answer"] = False
r = tools["run"].run({"command": "echo nope"}, ctx)
ck("declined run does not execute", not r.ok and "declined" in r.summary, str(r))
r = tools["run"].run({"command": "rm -rf /"}, ctx)
ck("catastrophic run refused outright", not r.ok and "refused" in r.output, str(r))

print("\n== yolo mode skips approval ==")
yctx = T.ToolContext(cwd=ws, approve=lambda k, p, d: False, approval_mode="yolo")
r = tools["run"].run({"command": "echo y"}, yctx)
ck("yolo runs without approval", r.ok and "y" in r.output, str(r))
r = tools["run"].run({"command": "mkfs.ext4 /dev/sda"}, yctx)
ck("yolo STILL refuses catastrophic", not r.ok, str(r))

print("\n== todo ==")
r = tools["todo"].run({"items": [{"text": "a", "status": "done"},
                                 {"text": "b", "status": "doing"}]}, ctx)
ck("todo ok + normalised", r.ok and len(r.detail["items"]) == 2, str(r))

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
