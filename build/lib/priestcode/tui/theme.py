"""theme.py — Textual themes for Priest Code.

Built on Textual's native theme system, so the command palette (ctrl+p →
"Change theme") switches them LIVE, and every widget plus the rendered
transcript re-tints instantly. Each theme also carries two custom variables the
transcript reads directly: `pc-dim` (muted text) and `pc-user` (the operator's
own line).
"""

from __future__ import annotations

from typing import Dict, List

from textual.theme import Theme


PRIEST = Theme(
    name="priest",
    primary="#d97757",      # coral — the accent
    secondary="#a78bfa",    # violet
    accent="#d97757",
    foreground="#eae7f7",
    background="#0c0a16",   # deep indigo ground
    surface="#151228",
    panel="#1c1836",
    success="#5ac37d",
    warning="#e0a34e",
    error="#e5556f",
    dark=True,
    variables={"pc-dim": "#8d87ad", "pc-user": "#a78bfa",
               "block-cursor-text-style": "none"},
)

OPENCODE = Theme(
    name="opencode",
    primary="#3fb1c9",      # teal
    secondary="#7ee787",
    accent="#3fb1c9",
    foreground="#e6edf3",
    background="#0d1117",
    surface="#141b24",
    panel="#1b2430",
    success="#3fb950",
    warning="#d29922",
    error="#f85149",
    dark=True,
    variables={"pc-dim": "#7d8791", "pc-user": "#58a6ff",
               "block-cursor-text-style": "none"},
)

MONO = Theme(
    name="mono",
    primary="#ffffff",
    secondary="#bdbdbd",
    accent="#ffffff",
    foreground="#e6e6e6",
    background="#0a0a0a",
    surface="#141414",
    panel="#1c1c1c",
    success="#9fe6a0",
    warning="#e6cf8a",
    error="#e69a9a",
    dark=True,
    variables={"pc-dim": "#8a8a8a", "pc-user": "#bdbdbd",
               "block-cursor-text-style": "none"},
)

ALL: List[Theme] = [PRIEST, OPENCODE, MONO]
BY_NAME: Dict[str, Theme] = {t.name: t for t in ALL}
DEFAULT = "priest"


def names() -> List[str]:
    return [t.name for t in ALL]
