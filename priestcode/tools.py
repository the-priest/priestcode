"""tools.py — the coding agent's hands.

A small registry of well-behaved tools. Each one:
  • has a `name` and a `description` (the description is what the model reads
    in the system prompt, with an example call),
  • validates its own arguments and returns a structured `ToolResult` rather
    than raising,
  • produces a one-line `summary` for the transparent UI, and, for edits, a
    unified `diff` so the operator sees exactly what changed.

Every path is resolved under the workspace root and refused if it escapes it —
a coding agent has no business writing outside the project it was pointed at.
"""

from __future__ import annotations

import difflib
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from .safety import catastrophic


@dataclass
class ToolResult:
    ok: bool
    summary: str = ""
    output: str = ""                    # text returned to the model
    detail: Dict[str, Any] = field(default_factory=dict)
    diff: Optional[Dict[str, Any]] = None


@dataclass
class ToolContext:
    cwd: Path
    approve: Callable[[str, str, str], bool]   # (kind, prompt, detail) -> bool
    approval_mode: str = "diff"                # "diff" | "confirm" | "yolo"
    permissions: Any = None                    # permissions.Ruleset | None

    def gate(self, action: str, resource: str, prompt: str,
             detail: str) -> Optional[str]:
        """Decide whether a side effect may proceed. Returns None to proceed,
        or a short refusal string to block. A permission ruleset wins first;
        with no matching rule the approval MODE decides."""
        eff = self.permissions.evaluate(action, resource) if self.permissions else None
        if eff == "deny":
            return f"blocked by permission policy ({action} {resource})"
        if eff == "allow":
            return None
        if eff == "ask":
            return None if self.approve(action, prompt, detail) else "declined"
        # no rule → approval mode
        if self.approval_mode == "yolo":
            return None
        is_shell = action in ("bash", "run", "shell", "command")
        if is_shell:
            return None if self.approve(action, prompt, detail) else "declined"
        # a write/edit: diff mode auto-applies, confirm mode asks
        if self.approval_mode == "confirm":
            return None if self.approve(action, prompt, detail) else "declined"
        return None


# ── path safety ──────────────────────────────────────────────────────
def _resolve(ctx: ToolContext, path: str) -> Path:
    p = (ctx.cwd / os.path.expanduser(path)).resolve() if not os.path.isabs(
        os.path.expanduser(path)) else Path(os.path.expanduser(path)).resolve()
    return p


def _inside(ctx: ToolContext, p: Path) -> bool:
    try:
        p.relative_to(ctx.cwd.resolve())
        return True
    except Exception:
        return False


def _rel(ctx: ToolContext, p: Path) -> str:
    try:
        return str(p.relative_to(ctx.cwd.resolve()))
    except Exception:
        return str(p)


# ── the Tool base ────────────────────────────────────────────────────
class Tool:
    name = ""
    description = ""      # includes an example: <tool name="x">{...}</tool> // desc

    def run(self, args: Dict[str, Any], ctx: ToolContext) -> ToolResult:
        raise NotImplementedError

    def summarize(self, args: Dict[str, Any]) -> str:
        return self.name


def _need(args, *keys) -> Optional[str]:
    for k in keys:
        if k not in args or args[k] is None:
            return f"missing required argument {k!r}"
    return None


# ── read_file ────────────────────────────────────────────────────────
class ReadFile(Tool):
    name = "read_file"
    description = ('read a file. <tool name="read_file">{"path": "src/app.py"}'
                  '</tool>  // optional "offset" and "limit" (line numbers)')

    def summarize(self, args):
        return f'read {args.get("path", "?")}'

    def run(self, args, ctx):
        err = _need(args, "path")
        if err:
            return ToolResult(False, output=err)
        p = _resolve(ctx, args["path"])
        if not _inside(ctx, p):
            return ToolResult(False, output="path is outside the workspace")
        if not p.is_file():
            return ToolResult(False, output=f"no such file: {_rel(ctx, p)}")
        try:
            text = p.read_text("utf-8", errors="replace")
        except Exception as e:
            return ToolResult(False, output=f"cannot read: {e}")
        lines = text.splitlines()
        off = int(args.get("offset", 0) or 0)
        lim = args.get("limit")
        sel = lines[off: off + int(lim)] if lim else lines[off:]
        numbered = "\n".join(f"{off + i + 1:>5}│{ln}"
                             for i, ln in enumerate(sel))
        return ToolResult(True, summary=f"{len(sel)} lines",
                          output=numbered or "(empty file)")


# ── write_file ───────────────────────────────────────────────────────
class WriteFile(Tool):
    name = "write_file"
    description = ('write a whole file (creates parent dirs; use for NEW files '
                  'and full rewrites). '
                  '<tool name="write_file">{"path": "index.html", "content": '
                  '"<!DOCTYPE html>..."}</tool>  // "mode":"create" (default) '
                  'or "append"')

    def summarize(self, args):
        return f'write {args.get("path", "?")}'

    def run(self, args, ctx):
        err = _need(args, "path", "content")
        if err:
            return ToolResult(False, output=err)
        p = _resolve(ctx, args["path"])
        if not _inside(ctx, p):
            return ToolResult(False, output="path is outside the workspace")
        content = args["content"]
        mode = str(args.get("mode", "create")).strip().lower()
        if mode in ("create", "create_new", "new", "replace", "write", "overwrite"):
            mode = "replace"
        elif mode in ("append", "a", "add"):
            mode = "append"
        else:
            return ToolResult(False, output=f"unknown mode {mode!r}: "
                              "use 'create' (default) or 'append'")
        existed = p.is_file()
        old = p.read_text("utf-8", errors="replace") if existed else ""
        new = (old + content) if mode == "append" else content
        blocked = ctx.gate("edit", _rel(ctx, p), f"Write {_rel(ctx, p)}?",
                           _rel(ctx, p))
        if blocked:
            return ToolResult(False, summary=blocked,
                              output=f"not written ({blocked}).")
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(new, "utf-8")
        except Exception as e:
            return ToolResult(False, output=f"cannot write: {e}")
        diff = _make_diff(_rel(ctx, p), old, new, created=not existed)
        verb = "created" if not existed else ("appended to" if mode == "append"
                                              else "wrote")
        return ToolResult(
            True, summary=f"{verb} {_rel(ctx, p)} (+{diff['added']}/-{diff['removed']})",
            output=f"{verb} {_rel(ctx, p)} — {len(new.splitlines())} lines",
            diff=diff, detail={"old": old if existed else None, "path": str(p)})


# ── edit_file (exact find/replace) ───────────────────────────────────
class EditFile(Tool):
    name = "edit_file"
    description = ('replace an exact string in a file (must match once unless '
                  '"all":true). <tool name="edit_file">{"path": "app.py", '
                  '"old": "def foo():", "new": "def foo(x):"}</tool>')

    def summarize(self, args):
        return f'edit {args.get("path", "?")}'

    def run(self, args, ctx):
        err = _need(args, "path", "old", "new")
        if err:
            return ToolResult(False, output=err)
        p = _resolve(ctx, args["path"])
        if not _inside(ctx, p):
            return ToolResult(False, output="path is outside the workspace")
        if not p.is_file():
            return ToolResult(False, output=f"no such file: {_rel(ctx, p)}")
        old_all = p.read_text("utf-8", errors="replace")
        old, new = args["old"], args["new"]
        n = old_all.count(old)
        if n == 0:
            return ToolResult(False, output="the 'old' string was not found "
                              "(it must match the file exactly, whitespace "
                              "included)")
        if n > 1 and not args.get("all"):
            return ToolResult(False, output=f"'old' matches {n} places — pass "
                              '"all":true to replace every one, or add more '
                              "context to make it unique")
        new_all = old_all.replace(old, new) if args.get("all") \
            else old_all.replace(old, new, 1)
        blocked = ctx.gate("edit", _rel(ctx, p), f"Edit {_rel(ctx, p)}?",
                           _rel(ctx, p))
        if blocked:
            return ToolResult(False, summary=blocked,
                              output=f"not edited ({blocked}).")
        try:
            p.write_text(new_all, "utf-8")
        except Exception as e:
            return ToolResult(False, output=f"cannot write: {e}")
        diff = _make_diff(_rel(ctx, p), old_all, new_all)
        return ToolResult(
            True,
            summary=f"edited {_rel(ctx, p)} (+{diff['added']}/-{diff['removed']})",
            output=f"edited {_rel(ctx, p)}", diff=diff,
            detail={"old": old_all, "path": str(p)})


# ── list_dir ─────────────────────────────────────────────────────────
class ListDir(Tool):
    name = "list_dir"
    description = ('list a directory. <tool name="list_dir">{"path": "."}</tool>')

    def summarize(self, args):
        return f'list {args.get("path", ".")}'

    def run(self, args, ctx):
        p = _resolve(ctx, args.get("path", "."))
        if not _inside(ctx, p) or not p.is_dir():
            return ToolResult(False, output=f"not a directory: {args.get('path')}")
        rows = []
        for e in sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name)):
            if e.name.startswith(".") and e.name not in (".gitignore",):
                continue
            rows.append(("dir " if e.is_dir() else "file") + " " + e.name)
        return ToolResult(True, summary=f"{len(rows)} entries",
                          output="\n".join(rows) or "(empty)")


# ── tree ─────────────────────────────────────────────────────────────
class Tree(Tool):
    name = "tree"
    description = ('a compact recursive file tree. <tool name="tree">{"path": '
                  '".", "depth": 3}</tool>')
    _SKIP = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist",
             "build", ".mypy_cache", ".ruff_cache", ".pytest_cache"}

    def summarize(self, args):
        return f'tree {args.get("path", ".")}'

    def run(self, args, ctx):
        root = _resolve(ctx, args.get("path", "."))
        if not _inside(ctx, root) or not root.is_dir():
            return ToolResult(False, output="not a directory")
        maxd = int(args.get("depth", 3) or 3)
        out: List[str] = []
        count = [0]

        def walk(d: Path, prefix: str, depth: int):
            if depth > maxd or count[0] > 800:
                return
            entries = [e for e in sorted(d.iterdir(),
                       key=lambda x: (x.is_file(), x.name))
                       if e.name not in self._SKIP and not e.name.startswith(".")]
            for e in entries:
                count[0] += 1
                out.append(f"{prefix}{e.name}{'/' if e.is_dir() else ''}")
                if e.is_dir():
                    walk(e, prefix + "  ", depth + 1)

        out.append(f"{root.name}/")
        walk(root, "  ", 1)
        return ToolResult(True, summary=f"{count[0]} entries",
                          output="\n".join(out))


# ── glob ─────────────────────────────────────────────────────────────
class Glob(Tool):
    name = "glob"
    description = ('find files by glob. <tool name="glob">{"pattern": '
                  '"**/*.py"}</tool>')

    def summarize(self, args):
        return f'glob {args.get("pattern", "?")}'

    def run(self, args, ctx):
        err = _need(args, "pattern")
        if err:
            return ToolResult(False, output=err)
        root = ctx.cwd.resolve()
        hits = []
        try:
            it = root.glob(args["pattern"])          # pathlib handles **
        except Exception as e:
            return ToolResult(False, output=f"bad glob: {e}")
        for pth in it:
            if any(s in pth.parts for s in Tree._SKIP):
                continue
            if pth.is_file():
                hits.append(str(pth.relative_to(root)))
            if len(hits) > 500:
                break
        return ToolResult(True, summary=f"{len(hits)} files",
                          output="\n".join(sorted(hits)) or "(no matches)")


# ── grep ─────────────────────────────────────────────────────────────
class Grep(Tool):
    name = "grep"
    description = ('search file contents with a regex. <tool name="grep">'
                  '{"pattern": "def \\\\w+", "glob": "**/*.py"}</tool>')

    def summarize(self, args):
        return f'grep {args.get("pattern", "?")!r}'

    def run(self, args, ctx):
        err = _need(args, "pattern")
        if err:
            return ToolResult(False, output=err)
        try:
            rx = re.compile(args["pattern"])
        except re.error as e:
            return ToolResult(False, output=f"bad regex: {e}")
        globpat = args.get("glob", "**/*")
        root = ctx.cwd.resolve()
        rows: List[str] = []
        try:
            candidates = root.glob(globpat)          # pathlib handles **
        except Exception as e:
            return ToolResult(False, output=f"bad glob: {e}")
        for pth in candidates:
            if any(s in pth.parts for s in Tree._SKIP) or not pth.is_file():
                continue
            try:
                for i, ln in enumerate(pth.read_text("utf-8", "replace").splitlines(), 1):
                    if rx.search(ln):
                        rows.append(f"{pth.relative_to(root)}:{i}: {ln.strip()[:200]}")
                        if len(rows) > 300:
                            break
            except Exception:
                continue
            if len(rows) > 300:
                break
        return ToolResult(True, summary=f"{len(rows)} matches",
                          output="\n".join(rows) or "(no matches)")


# ── run (shell) ──────────────────────────────────────────────────────
class Run(Tool):
    name = "run"
    description = ('run a shell command in the workspace. <tool name="run">'
                  '{"command": "python -m pytest -q"}</tool>  // asks before '
                  'running unless approval is off; catastrophic commands are '
                  'always refused')

    def summarize(self, args):
        return f'run: {args.get("command", "?")}'

    def run(self, args, ctx):
        err = _need(args, "command")
        if err:
            return ToolResult(False, output=err)
        cmd = args["command"]
        reason = catastrophic(cmd)
        if reason:
            return ToolResult(False, summary="refused (catastrophic)",
                              output=f"refused: {reason}. This is never run, "
                              "with no override.")
        blocked = ctx.gate("bash", cmd, "Run this command?", cmd)
        if blocked:
            return ToolResult(False, summary=blocked,
                              output=f"the command was not run ({blocked}).")
        timeout = int(args.get("timeout", 120) or 120)
        try:
            proc = subprocess.run(cmd, shell=True, cwd=str(ctx.cwd),
                                  capture_output=True, text=True,
                                  timeout=timeout)
        except subprocess.TimeoutExpired:
            return ToolResult(False, summary=f"timed out ({timeout}s)",
                              output=f"command timed out after {timeout}s")
        except Exception as e:
            return ToolResult(False, output=f"failed to run: {e}")
        out = (proc.stdout or "")
        if proc.stderr:
            out += ("\n[stderr]\n" + proc.stderr)
        out = out.strip()
        if len(out) > 20000:
            out = out[:20000] + "\n… (truncated)"
        ok = proc.returncode == 0
        return ToolResult(ok, summary=f"exit {proc.returncode}",
                          output=out or f"(no output) exit {proc.returncode}",
                          detail={"code": proc.returncode})


# ── todo (task tracking, like OpenCode's todo panel) ─────────────────
class TodoWrite(Tool):
    name = "todo"
    description = ('track a task list the operator can see. <tool name="todo">'
                  '{"items": [{"text": "write parser", "status": "doing"}, '
                  '{"text": "add tests", "status": "todo"}]}</tool>  // status: '
                  'todo | doing | done')

    def summarize(self, args):
        return f'{len(args.get("items", []))} tasks'

    def run(self, args, ctx):
        items = args.get("items") or []
        norm = []
        for it in items:
            if isinstance(it, dict):
                norm.append({"text": str(it.get("text", "")),
                             "status": str(it.get("status", "todo"))})
            else:
                norm.append({"text": str(it), "status": "todo"})
        done = sum(1 for i in norm if i["status"] == "done")
        return ToolResult(True, summary=f"{done}/{len(norm)} done",
                          output="task list updated",
                          detail={"items": norm})


# ── helpers ──────────────────────────────────────────────────────────
def _make_diff(path: str, old: str, new: str, created: bool = False
               ) -> Dict[str, Any]:
    ud = list(difflib.unified_diff(old.splitlines(), new.splitlines(),
                                   fromfile=("/dev/null" if created else path),
                                   tofile=path, lineterm=""))
    added = sum(1 for ln in ud if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in ud if ln.startswith("-") and not ln.startswith("---"))
    return {"path": path, "unified": "\n".join(ud), "added": added,
            "removed": removed, "created": created}


# ── registry ─────────────────────────────────────────────────────────
def default_tools() -> Dict[str, Tool]:
    tools = [ReadFile(), WriteFile(), EditFile(), ListDir(), Tree(), Glob(),
             Grep(), Run(), TodoWrite()]
    return {t.name: t for t in tools}


def tool_contract(tools: Dict[str, Tool]) -> str:
    """The block of the system prompt that documents every tool + example."""
    lines = []
    for t in tools.values():
        lines.append(f"- {t.description}")
    return "\n".join(lines)
