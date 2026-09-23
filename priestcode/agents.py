"""agents.py — named agents (modes), like OpenCode's build / plan / custom.

An agent bundles a role: an optional extra system prompt, which tools it may
use, an optional model override, and a step budget. Two ship built in:

  • build — the default. Every tool; edits, runs, iterates.
  • plan  — read-only. Only the read/search tools, no write/edit/run. For
            "figure out what's wrong and propose a fix" without touching a file.

Custom agents come from the project config under `agents`, e.g. a `reviewer`
that can read but not edit. Switch agents from the command palette or `/agent`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .tools import Tool, default_tools


_READ_ONLY = ("read_file", "list_dir", "tree", "glob", "grep", "todo")


@dataclass
class Agent:
    name: str
    description: str = ""
    system: str = ""                       # extra system prompt
    tools: Optional[List[str]] = None      # None = all; else an allow-list
    model: str = ""                        # optional "provider/model" override
    steps: int = 0                         # 0 = use the config default
    color: str = ""

    def toolset(self) -> Dict[str, Tool]:
        allt = default_tools()
        if self.tools is None:
            return allt
        return {n: t for n, t in allt.items() if n in self.tools}


BUILTIN: Dict[str, Agent] = {
    "build": Agent(
        "build", "Full coding agent — edits, runs, iterates until it passes.",
        system="", tools=None, color="accent"),
    "plan": Agent(
        "plan", "Read-only. Investigate and propose; never touches a file.",
        system=("You are in PLAN mode. You may read, search and analyse, but you "
                "MUST NOT write, edit or run anything — those tools are not "
                "available. Produce a clear, concrete plan or diagnosis: which "
                "files, which changes, and why. The operator will switch you to "
                "build mode to execute."),
        tools=list(_READ_ONLY), color="secondary"),
}

DEFAULT = "build"


def from_config(raw: dict) -> Dict[str, Agent]:
    """Merge custom agents from config over the built-ins."""
    agents = dict(BUILTIN)
    for name, spec in (raw or {}).items():
        if not isinstance(spec, dict) or spec.get("disabled"):
            continue
        base = agents.get(name)
        tools = spec.get("tools")
        agents[name] = Agent(
            name=name,
            description=spec.get("description", base.description if base else ""),
            system=spec.get("system", base.system if base else ""),
            tools=list(tools) if isinstance(tools, list) else (
                base.tools if base else None),
            model=spec.get("model", ""),
            steps=int(spec.get("steps", 0) or 0),
            color=spec.get("color", ""))
    return agents


def get(name: str, configured: Dict[str, Agent] = None) -> Agent:
    pool = configured or BUILTIN
    return pool.get(name) or pool.get(DEFAULT) or BUILTIN["build"]
