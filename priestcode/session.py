"""session.py — conversations persist across runs.

Each session is a JSON file under ~/.local/share/priestcode/sessions/, holding
the message list and a little metadata (title, model, workspace, timestamps).
Like OpenCode, you can resume the last session or pick one. Best-effort: a
corrupt or unreadable session never crashes the app.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


def data_dir() -> Path:
    root = os.environ.get("XDG_DATA_HOME") or str(Path.home() / ".local" / "share")
    d = Path(root) / "priestcode" / "sessions"
    return d


@dataclass
class Session:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    title: str = "untitled"
    workspace: str = ""
    provider: str = ""
    model: str = ""
    created: float = field(default_factory=time.time)
    updated: float = field(default_factory=time.time)
    messages: List[Dict[str, str]] = field(default_factory=list)

    def path(self) -> Path:
        return data_dir() / f"{self.id}.json"

    def save(self) -> None:
        self.updated = time.time()
        d = data_dir()
        try:
            d.mkdir(parents=True, exist_ok=True)
            self.path().write_text(json.dumps({
                "id": self.id, "title": self.title, "workspace": self.workspace,
                "provider": self.provider, "model": self.model,
                "created": self.created, "updated": self.updated,
                "messages": self.messages,
            }, indent=2), "utf-8")
        except Exception:
            pass

    def title_from(self, first_user_text: str) -> None:
        t = " ".join((first_user_text or "").split())[:60]
        self.title = t or "untitled"


def load(session_id: str) -> Optional[Session]:
    p = data_dir() / f"{session_id}.json"
    try:
        d = json.loads(p.read_text("utf-8"))
        return Session(id=d["id"], title=d.get("title", "untitled"),
                       workspace=d.get("workspace", ""),
                       provider=d.get("provider", ""), model=d.get("model", ""),
                       created=d.get("created", time.time()),
                       updated=d.get("updated", time.time()),
                       messages=d.get("messages", []))
    except Exception:
        return None


def recent(limit: int = 20) -> List[Dict[str, Any]]:
    d = data_dir()
    rows: List[Dict[str, Any]] = []
    if not d.exists():
        return rows
    for f in d.glob("*.json"):
        try:
            j = json.loads(f.read_text("utf-8"))
            rows.append({"id": j.get("id", f.stem),
                         "title": j.get("title", "untitled"),
                         "updated": j.get("updated", 0),
                         "workspace": j.get("workspace", ""),
                         "model": j.get("model", "")})
        except Exception:
            continue
    rows.sort(key=lambda r: r.get("updated", 0), reverse=True)
    return rows[:limit]


def latest() -> Optional[str]:
    r = recent(1)
    return r[0]["id"] if r else None
