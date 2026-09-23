"""safety.py — the floor under the shell tool.

Priest Code runs commands as you. Most of that is normal work and should not be
nagged about. But a small set of commands are irreversible and catastrophic —
wiping a disk, `rm -rf /`, a fork bomb, piping the internet into a shell — and
those are refused outright, with no "run anyway", regardless of approval mode
(even YOLO). Everything else flows through the ordinary approval path.

The matcher normalises the command first so the obvious evasions do not work:
`$IFS` splitting, `sh -c '...'` wrapping, quotes and backslashes inside a word.
It errs toward *allowing* ordinary work — a false refusal on real work is its
own bug — so it targets a tight, unambiguous set.
"""

from __future__ import annotations

import re
from typing import Optional


def _normalise(cmd: str) -> str:
    """Collapse a command to a canonical form for matching."""
    c = cmd or ""
    # unwrap a single sh/bash -c "..."  (one level is enough to catch the trick)
    m = re.match(r"""\s*(?:sudo\s+|doas\s+)?(?:ba|da|z|)sh\s+-c\s+(['"])(.*)\1\s*$""",
                 c, re.S)
    if m:
        c = m.group(2)
    # $IFS and ${IFS} used as a separator → a space
    c = re.sub(r"\$\{?IFS\}?", " ", c)
    # strip quotes and backslashes that only serve to break up a word
    c = c.replace('"', "").replace("'", "").replace("\\", "")
    # collapse whitespace
    c = re.sub(r"\s+", " ", c).strip().lower()
    return c


# Each entry: (compiled regex over the normalised command, why it is refused).
_CATASTROPHIC = [
    (re.compile(r"\brm\s+(-[a-z]*\s+)*-[a-z]*[rf][a-z]*\b.*\s(/|~|/\*|\$home)\s*$"),
     "recursive delete of a root/home path"),
    (re.compile(r"\brm\s+-[a-z]*[rf][a-z]*\s+(/|/\*|~|~/\*)\s*$"),
     "recursive delete of /"),
    (re.compile(r"\bmkfs\b"), "formatting a filesystem"),
    (re.compile(r"\bdd\b.*\bof=/dev/(sd|nvme|vd|hd|mmcblk|disk)"),
     "writing raw to a block device"),
    (re.compile(r">\s*/dev/(sd|nvme|vd|hd|mmcblk|disk)"),
     "redirecting onto a block device"),
    (re.compile(r"\b(shred|wipefs)\b.*\s/dev/"), "wiping a device"),
    (re.compile(r":\s*\(\s*\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:"),
     "fork bomb"),
    (re.compile(r"\b(curl|wget|fetch)\b.*\|\s*(sudo\s+)?(ba|da|z|)sh\b"),
     "piping a download straight into a shell"),
    (re.compile(r"\bchmod\s+-r\s+0*\s+/\s*$"), "chmod 0 on /"),
    (re.compile(r"\b(halt|poweroff|shutdown|reboot)\b"),
     "powering off / rebooting the machine"),
    (re.compile(r"\bgit\b.*\bpush\b.*--force.*\b(origin\s+)?(main|master)\b"),
     "force-pushing over main/master"),
]


def catastrophic(cmd: str) -> Optional[str]:
    """Return a reason string if the command is catastrophic, else None."""
    if not cmd or not cmd.strip():
        return None
    norm = _normalise(cmd)
    for rx, why in _CATASTROPHIC:
        if rx.search(norm):
            return why
    return None


def is_catastrophic(cmd: str) -> bool:
    return catastrophic(cmd) is not None
