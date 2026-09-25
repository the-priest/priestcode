"""skills.py — the skill library and the `skill` tool.

A *skill* is a packaged piece of expertise: a short markdown file with
frontmatter (name, description, category, tags) and a body of concrete
instructions — a checklist, the commands, the pitfalls, a worked example.
This is the same idea as Claude Code / OpenCode skills, with the same
progressive-disclosure contract:

  • the model always sees a compact INDEX (category → names + one-liners),
    which is cheap;
  • it loads a skill's full BODY on demand with the `skill` tool, so only the
    handful it actually needs cost context.

Skills are discovered from three places, nearest wins on a name clash:
  1. the bundled library shipped with Priest Code  (priestcode/skills/**)
  2. the user's global skills                        (~/.config/priestcode/skills/**)
  3. the project's skills                            (<repo>/.priest/skills/**)

Everything is best-effort: an unreadable or malformed skill is skipped, never
fatal. stdlib only.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .tools import Tool, ToolContext, ToolResult


# ── the skill record ──────────────────────────────────────────────────
@dataclass
class Skill:
    name: str
    description: str
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    body: str = ""
    source: str = "bundled"          # bundled | user | project
    path: Optional[Path] = None


# ── frontmatter parsing (a tiny, dependency-free YAML subset) ──────────
_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)


def _parse_skill(text: str, fallback_name: str) -> Optional[Skill]:
    m = _FM_RE.match(text)
    if not m:
        # no frontmatter — treat the first heading as the name, rest as body
        body = text.strip()
        first = next((ln for ln in body.splitlines() if ln.strip()), fallback_name)
        name = re.sub(r"^#+\s*", "", first).strip() or fallback_name
        return Skill(name=name, description=first[:200], body=body)
    front, body = m.group(1), m.group(2).strip()
    meta: Dict[str, object] = {}
    for line in front.splitlines():
        if not line.strip() or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip().lower()
        val = val.strip()
        if key == "tags":
            # [a, b, c] or a, b, c
            val = val.strip("[]")
            meta[key] = [t.strip().strip("'\"") for t in val.split(",") if t.strip()]
        else:
            meta[key] = val.strip("'\"")
    name = str(meta.get("name") or fallback_name).strip()
    if not name:
        return None
    return Skill(
        name=name,
        description=str(meta.get("description") or "")[:400],
        category=str(meta.get("category") or "general"),
        tags=list(meta.get("tags") or []),
        body=body,
    )


# ── discovery ─────────────────────────────────────────────────────────
def _bundled_dir() -> Path:
    return Path(__file__).resolve().parent / "skills"


def _user_dir() -> Path:
    root = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(root) / "priestcode" / "skills"


def _scan(root: Path, source: str, into: Dict[str, Skill]) -> None:
    if not root.is_dir():
        return
    for p in sorted(root.rglob("*.md")):
        try:
            sk = _parse_skill(p.read_text("utf-8", errors="replace"), p.stem)
        except Exception:
            continue
        if not sk:
            continue
        sk.source = source
        sk.path = p
        # infer category from the folder layout if not declared
        if sk.category == "general":
            rel = p.relative_to(root).parts
            if len(rel) > 1:
                sk.category = "/".join(rel[:-1])
        into[sk.name] = sk          # nearer source overwrites (project last)


def load_skills(workspace: Optional[Path] = None) -> Dict[str, Skill]:
    """All skills, keyed by name. Order of scan = order of precedence:
    bundled first, then user, then project — later writes win a name clash."""
    skills: Dict[str, Skill] = {}
    _scan(_bundled_dir(), "bundled", skills)
    _scan(_user_dir(), "user", skills)
    if workspace:
        _scan(Path(workspace) / ".priest" / "skills", "project", skills)
    return skills


# ── the compact index that goes into the system prompt ─────────────────
def skills_index(skills: Dict[str, Skill], max_inline: int = 0,
                 names: bool = True) -> str:
    """A category-grouped catalogue for the system prompt.

    The default (names=True, max_inline=0) lists categories with a sample of
    names. `names=False` is the LEAN form — just categories and counts, ~700
    chars instead of ~6k — since the `skill` tool can search/list the actual
    names on demand. That trims well over a thousand tokens off EVERY request,
    at the cost of one `skill search` round-trip when a skill is actually needed.
    A positive max_inline inlines that many `name — description` lines per
    category (verbose)."""
    if not skills:
        return ""
    by_cat: Dict[str, List[Skill]] = {}
    for sk in skills.values():
        by_cat.setdefault(sk.category, []).append(sk)
    if not names and max_inline <= 0:
        cats = ", ".join(f"{c} ({len(v)})" for c, v in sorted(by_cat.items()))
        return (f"{len(skills)} skills installed. Find and load one with the "
                f"`skill` tool (search by task, or list a category) BEFORE doing "
                f"the kind of work it covers. Categories: {cats}.")
    lines = [f"{len(skills)} skills are installed, grouped by category. Use the "
             "`skill` tool to find and load the ones a task needs — load a skill "
             "BEFORE doing the kind of work it covers."]
    for cat in sorted(by_cat):
        items = sorted(by_cat[cat], key=lambda s: s.name)
        if max_inline > 0:
            lines.append(f"\n## {cat} ({len(items)})")
            for sk in items[:max_inline]:
                lines.append(f"- {sk.name} — {sk.description}")
            if len(items) > max_inline:
                lines.append(f"  …and {len(items) - max_inline} more "
                             f"(`skill list {cat}`)")
        else:
            names_s = ", ".join(s.name for s in items[:12])
            more = f", +{len(items) - 12} more" if len(items) > 12 else ""
            lines.append(f"- {cat} ({len(items)}): {names_s}{more}")
    return "\n".join(lines)


def _score(sk: Skill, q: str) -> int:
    q = q.lower()
    terms = [t for t in re.split(r"\W+", q) if t]
    hay = (sk.name + " " + sk.description + " " + " ".join(sk.tags) + " "
           + sk.category).lower()
    score = 0
    if q and q in hay:
        score += 5
    for t in terms:
        if t in sk.name.lower():
            score += 4
        elif t in " ".join(sk.tags).lower():
            score += 3
        elif t in hay:
            score += 1
    return score


# ── the `skill` tool ──────────────────────────────────────────────────
class SkillTool(Tool):
    name = "skill"
    description = ('find and load a skill (packaged expertise). '
                  '<tool name="skill">{"action":"search","query":"sql injection"}'
                  '</tool> — then '
                  '<tool name="skill">{"action":"load","name":"..."}</tool>')
    summary = ("Search, list, or load a skill — packaged expertise (a checklist, "
               "commands, pitfalls) for a kind of coding/security work.")
    params = {
        "action": {"type": "string", "enum": ["search", "list", "load"],
                   "description": "search by query, list a category, or load by name"},
        "query": {"type": "string", "description": "for action=search"},
        "category": {"type": "string", "description": "for action=list"},
        "name": {"type": "string", "description": "for action=load (exact skill name)"},
    }
    required = ("action",)

    def __init__(self, skills: Dict[str, Skill]):
        self._skills = skills

    def summarize(self, args):
        a = args.get("action", "?")
        tgt = args.get("name") or args.get("query") or args.get("category") or ""
        return f"skill {a} {tgt}".strip()

    def run(self, args, ctx: ToolContext) -> ToolResult:
        action = (args.get("action") or "").strip().lower()
        sk = self._skills

        if action == "load":
            name = (args.get("name") or "").strip()
            hit = sk.get(name)
            if not hit:
                # tolerate a near-miss: case-insensitive / slug match
                low = name.lower()
                hit = next((s for s in sk.values()
                            if s.name.lower() == low), None)
            if not hit:
                sug = sorted(sk, key=lambda n: _score(sk[n], name),
                             reverse=True)[:5]
                return ToolResult(False, summary="no such skill",
                                  output=f"no skill named {name!r}. Closest: "
                                         f"{', '.join(sug) or '(none)'}. "
                                         f"Use action=search to find one.")
            head = f"# skill: {hit.name}\n({hit.category} · {hit.source})\n\n"
            return ToolResult(True, summary=f"loaded {hit.name}",
                              output=head + hit.body)

        if action == "list":
            cat = (args.get("category") or "").strip()
            items = [s for s in sk.values()
                     if not cat or s.category == cat
                     or s.category.startswith(cat + "/")]
            if not items:
                cats = sorted({s.category for s in sk.values()})
                return ToolResult(True, summary="categories",
                                  output="categories: " + ", ".join(cats))
            items.sort(key=lambda s: (s.category, s.name))
            rows = [f"- {s.name} [{s.category}] — {s.description}" for s in items[:80]]
            extra = f"\n…and {len(items) - 80} more" if len(items) > 80 else ""
            return ToolResult(True, summary=f"{len(items)} skills",
                              output="\n".join(rows) + extra)

        # default: search
        q = (args.get("query") or args.get("name") or "").strip()
        if not q:
            return ToolResult(False, output="search needs a query.")
        ranked = sorted(sk.values(), key=lambda s: _score(s, q), reverse=True)
        ranked = [s for s in ranked if _score(s, q) > 0][:12]
        if not ranked:
            return ToolResult(True, summary="no matches",
                              output=f"no skills matched {q!r}. Try `skill list`.")
        rows = [f"- {s.name} [{s.category}] — {s.description}" for s in ranked]
        return ToolResult(True, summary=f"{len(ranked)} matches",
                          output="matches (load one with action=load):\n"
                                 + "\n".join(rows))
