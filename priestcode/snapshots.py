"""snapshots.py — undo for the agent's file changes.

Before every write or edit, the previous state of the file (its full content,
or the fact that it did not exist) is pushed onto a stack. `/undo` pops the last
one and restores it — so an edit you did not want is one keystroke away from
being reversed, exactly like OpenCode's revert. In-memory and session-scoped;
it never touches git, so it composes with whatever VCS you use.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class Snapshot:
    path: Path
    old: Optional[str]        # None means the file did not exist before
    label: str = ""


@dataclass
class SnapshotStack:
    stack: List[Snapshot] = field(default_factory=list)
    limit: int = 200

    def push(self, path: Path, old: Optional[str], label: str = "") -> None:
        self.stack.append(Snapshot(Path(path), old, label))
        if len(self.stack) > self.limit:
            self.stack.pop(0)

    def can_undo(self) -> bool:
        return bool(self.stack)

    def undo(self) -> Optional[str]:
        """Restore the most recent snapshot. Returns a human message, or None
        if there is nothing to undo."""
        if not self.stack:
            return None
        snap = self.stack.pop()
        try:
            if snap.old is None:
                # it did not exist before → remove what was created
                if snap.path.is_file():
                    snap.path.unlink()
                return f"reverted (removed) {snap.label or snap.path.name}"
            snap.path.parent.mkdir(parents=True, exist_ok=True)
            snap.path.write_text(snap.old, "utf-8")
            return f"reverted {snap.label or snap.path.name}"
        except Exception as e:
            return f"could not revert {snap.path.name}: {e}"
