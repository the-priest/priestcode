"""permissions.py — a granular, ordered permission ruleset.

OpenCode replaces the blunt "ask about everything" toggle with an ordered list
of rules like:

    [ {action: "bash", resource: "git status", effect: "allow"},
      {action: "bash", resource: "*",          effect: "ask"},
      {action: "edit", resource: "*",          effect: "allow"} ]

Priest Code does the same. Each rule is `{action, resource, effect}` where
effect is allow | ask | deny. Rules are evaluated top to bottom and the FIRST
match wins, so put specific rules above general ones. `action` matches a tool
category ("bash"/"run", "edit"/"write", "read", or "*"); `resource` is a glob
matched against the command string or the file path. When no rule matches, the
approval MODE decides (diff/confirm/yolo), so an empty ruleset behaves exactly
like before.
"""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass
from typing import List, Optional


_ALIASES = {
    "run": "bash", "shell": "bash", "command": "bash",
    "write": "edit", "write_file": "edit", "edit_file": "edit",
    "read_file": "read", "list_dir": "read", "tree": "read", "grep": "read",
    "glob": "read",
}


def _canon(action: str) -> str:
    return _ALIASES.get(action, action)


@dataclass
class Rule:
    action: str
    resource: str
    effect: str          # "allow" | "ask" | "deny"


class Ruleset:
    def __init__(self, rules: Optional[List[Rule]] = None):
        self.rules = rules or []

    @classmethod
    def from_config(cls, raw) -> "Ruleset":
        rules = []
        for r in (raw or []):
            if not isinstance(r, dict):
                continue
            eff = str(r.get("effect", "ask")).lower()
            if eff not in ("allow", "ask", "deny"):
                eff = "ask"
            rules.append(Rule(_canon(str(r.get("action", "*")).lower()),
                              str(r.get("resource", "*")), eff))
        return cls(rules)

    def evaluate(self, action: str, resource: str) -> Optional[str]:
        """Return 'allow' | 'ask' | 'deny', or None if no rule matches."""
        act = _canon((action or "").lower())
        for r in self.rules:
            if r.action not in (act, "*"):
                continue
            if r.resource in ("*", "") or fnmatch.fnmatch(resource or "", r.resource):
                return r.effect
        return None

    def __bool__(self) -> bool:
        return bool(self.rules)
