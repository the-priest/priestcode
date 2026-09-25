"""context.py — making the agent project-aware.

Three things OpenCode does that turn a chat model into a coding agent, and that
Priest Code does too:

  1. Ambient instructions. Files like AGENTS.md, CLAUDE.md, .cursor/rules/*.md
     and .priestrules are automatically folded into the system prompt, plus any
     paths/globs the project config lists under `instructions`. This is how the
     agent learns your conventions without being told every time.

  2. Config discovery. A `priestcode.json` (or `.priestcode/config.json`) is
     found by walking up from the working directory and merged over the global
     config — so a repo can pin its model, agent, permissions and instructions.

  3. @-mentions. `@path/to/file` in a prompt is expanded inline to that file's
     contents, so you can point the model at exactly what matters.

All of it is best-effort: a missing or unreadable file is skipped, never fatal.
"""

from __future__ import annotations

import glob as _glob
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


# Instruction files auto-discovered in the project root (in priority order).
_INSTRUCTION_FILES = ("AGENTS.md", "CLAUDE.md", ".priestrules", ".cursorrules")
_INSTRUCTION_GLOBS = (".cursor/rules/*.md", ".priest/rules/*.md")

_CONFIG_NAMES = ("priestcode.json", ".priestcode/config.json", "priestcode.jsonc")

_MAX_INSTR_BYTES = 24000
_MAX_MENTION_BYTES = 20000


def find_project_config(cwd: Path) -> Tuple[Dict, List[Path]]:
    """Walk up from cwd, merging every priestcode config found (closest wins).
    Returns (merged_dict, files_used)."""
    merged: Dict = {}
    used: List[Path] = []
    chain = [cwd] + list(cwd.parents)
    # farthest-first so nearer files override
    for d in reversed(chain):
        for name in _CONFIG_NAMES:
            p = d / name
            if p.is_file():
                try:
                    text = p.read_text("utf-8")
                    text = _strip_jsonc(text)
                    data = json.loads(text)
                    if isinstance(data, dict):
                        merged = _deep_merge(merged, data)
                        used.append(p)
                except Exception:
                    pass
    return merged, used


def _strip_jsonc(text: str) -> str:
    # remove // line comments and /* */ block comments (naive but fine for config)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"(?m)//.*$", "", text)
    return text


def _deep_merge(a: Dict, b: Dict) -> Dict:
    out = dict(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_instructions(cwd: Path, extra_sources: List[str] = None) -> str:
    """Gather ambient instructions from the well-known files, the configured
    sources, and return them as one block for the system prompt (bounded)."""
    parts: List[str] = []
    seen = set()

    def add(path: Path, label: str = ""):
        try:
            rp = path.resolve()
            if rp in seen or not rp.is_file():
                return
            seen.add(rp)
            body = rp.read_text("utf-8", errors="replace").strip()
            if body:
                name = label or str(rp.relative_to(cwd) if _under(rp, cwd) else rp.name)
                parts.append(f"## from {name}\n{body}")
        except Exception:
            pass

    for name in _INSTRUCTION_FILES:
        add(cwd / name)
    for pat in _INSTRUCTION_GLOBS:
        for hit in sorted(_glob.glob(str(cwd / pat))):
            add(Path(hit))
    for src in (extra_sources or []):
        # a glob, a path, or (ignored) a URL
        if src.startswith(("http://", "https://")):
            continue
        for hit in sorted(_glob.glob(str(cwd / src))):
            add(Path(hit))

    text = "\n\n".join(parts)
    if len(text) > _MAX_INSTR_BYTES:
        text = text[:_MAX_INSTR_BYTES] + "\n… (instructions truncated)"
    return text


_MENTION_RE = re.compile(r"(?<!\w)@([\w./~-]+)")


def expand_mentions(text: str, cwd: Path) -> str:
    """Replace @path tokens with the file's contents appended as context."""
    hits = []
    for m in _MENTION_RE.finditer(text or ""):
        rel = m.group(1)
        p = (cwd / os.path.expanduser(rel)).resolve()
        if _under(p, cwd) and p.is_file():
            hits.append((rel, p))
    if not hits:
        return text
    blocks = [text.strip(), "", "Referenced files:"]
    for rel, p in hits:
        try:
            body = p.read_text("utf-8", errors="replace")
            if len(body) > _MAX_MENTION_BYTES:
                body = body[:_MAX_MENTION_BYTES] + "\n… (truncated)"
            blocks.append(f"\n--- {rel} ---\n{body}")
        except Exception:
            pass
    return "\n".join(blocks)


def _under(p: Path, root: Path) -> bool:
    try:
        p.resolve().relative_to(root.resolve())
        return True
    except Exception:
        return False
