"""config.py — user settings, API keys, and where they live.

Config is a plain JSON file at ~/.config/priestcode/config.json, written 0600
so the keys in it are not world-readable. Keys can also come from the
environment (per provider), so CI never has to write a file. A corrupt config
never crashes the app — it falls back to defaults.
"""

from __future__ import annotations

import json
import os
import stat
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict

from . import providers as P


def config_dir() -> Path:
    root = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(root) / "priestcode"


# priestcode provider id → the candidate provider id(s) OpenCode uses in its
# auth.json. Zen is provisioned automatically by OpenCode on first run (no manual
# account), stored under the "opencode" provider — which is why it "just works"
# there; we read that same credential.
_OPENCODE_PROVIDER = {
    "zen": ("opencode", "opencode-zen", "zen"),
    "gemini": ("google", "gemini", "google-generative-ai"),
    "groq": ("groq",),
    "openrouter": ("openrouter",),
    "siliconflow": ("siliconflow",),
    "openai": ("openai",),
}


def _opencode_auth_paths():
    paths = []
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        paths.append(Path(xdg) / "opencode" / "auth.json")
    home = Path.home()
    paths.append(home / ".local" / "share" / "opencode" / "auth.json")
    paths.append(home / ".config" / "opencode" / "auth.json")
    paths.append(home / "Library" / "Application Support" / "opencode"
                 / "auth.json")   # macOS
    return paths


def _extract_token(entry) -> str:
    if isinstance(entry, str) and entry.strip():
        return entry.strip()
    if isinstance(entry, dict):
        for k in ("key", "apiKey", "api_key", "access", "accessToken",
                  "access_token", "token"):
            v = entry.get(k)
            if v and isinstance(v, str):
                return v.strip()
    return ""


def opencode_key(provider_id: str) -> str:
    """Reuse a credential the user already has in OpenCode. Reads OpenCode's
    auth.json and returns the api key (or oauth access token) for the mapped
    provider — so Zen (which OpenCode auto-provisions) and any other provider set
    up there work here with no re-auth. Best-effort; '' if nothing usable."""
    candidates = _OPENCODE_PROVIDER.get(provider_id, ())
    for p in _opencode_auth_paths():
        try:
            if not p.is_file():
                continue
            data = json.loads(p.read_text("utf-8"))
            if not isinstance(data, dict):
                continue
            for oc in candidates:
                tok = _extract_token(data.get(oc))
                if tok:
                    return tok
        except Exception:
            continue
    return ""


def config_path() -> Path:
    return config_dir() / "config.json"


@dataclass
class Config:
    provider: str = P.DEFAULT_PROVIDER
    model: str = ""                      # "" → provider default
    # per-provider keys, keyed by provider id
    keys: Dict[str, str] = field(default_factory=dict)
    base_url_override: str = ""          # only for the generic openai provider
    # generation
    temperature: float = 0.3
    top_p: float = 0.95
    max_tokens: int = 16384              # room to write a whole file per turn
    # behaviour
    approval: str = "diff"               # "diff" | "confirm" | "yolo"
    max_steps: int = 50
    agent: str = "build"                 # active agent/mode: build | plan | …
    # presentation
    theme: str = "priest"                # see tui/theme.py
    stream: bool = True
    # project-derived (merged from priestcode.json; not persisted globally)
    instructions: list = field(default_factory=list)   # extra context sources
    permissions: list = field(default_factory=list)    # ordered rule dicts
    agents: dict = field(default_factory=dict)          # custom agent defs
    mcp: dict = field(default_factory=dict)             # mcp.servers config
    project_files: list = field(default_factory=list)   # config files used

    # ── derived ──
    def provider_obj(self) -> "P.Provider":
        return P.get_provider(self.provider) or P.get_provider(P.DEFAULT_PROVIDER)

    def model_id(self) -> str:
        prov = self.provider_obj()
        if self.model:
            return self.model
        return prov.default_model().id if prov.models else ""

    def model_obj(self):
        prov = self.provider_obj()
        return prov.model(self.model_id()) if prov else None

    def base_url(self) -> str:
        prov = self.provider_obj()
        if self.provider == "openai" and self.base_url_override:
            return self.base_url_override.rstrip("/")
        return prov.base_url.rstrip("/")

    def resolved_key(self) -> str:
        # 1. explicit stored key for this provider
        k = (self.keys.get(self.provider) or "").strip()
        if k:
            return k
        # 2. environment, per the provider's declared env vars
        prov = self.provider_obj()
        for env in prov.key_env:
            v = os.environ.get(env)
            if v:
                return v.strip()
        # 3. reuse a key the user already configured in OpenCode — so a provider
        #    that works there (Zen, Gemini, Groq, …) works here too, no re-auth.
        oc = opencode_key(self.provider)
        if oc:
            return oc
        # 4. a provider that serves models on a fixed public token, if any
        if prov.public_token:
            return prov.public_token
        return ""

    def has_key(self) -> bool:
        prov = self.provider_obj()
        return bool(self.resolved_key()) or not prov.needs_key


_PERSISTED = ("provider", "model", "keys", "base_url_override", "temperature",
              "top_p", "max_tokens", "approval", "max_steps", "theme", "stream",
              "agent")


def load(cwd=None) -> Config:
    """Load the global config, then layer any project config found by walking
    up from `cwd` over it (a repo's priestcode.json wins), then fold in the
    project's ambient instruction sources."""
    cfg = Config()
    p = config_path()
    try:
        if p.exists():
            data = json.loads(p.read_text("utf-8"))
            if isinstance(data, dict):
                for k in _PERSISTED:
                    if k in data and data[k] is not None:
                        setattr(cfg, k, data[k])
    except Exception:
        pass
    if cwd is not None:
        _apply_project(cfg, cwd)
    _coerce(cfg)
    return cfg


def _apply_project(cfg: Config, cwd) -> None:
    from pathlib import Path
    from . import context
    merged, used = context.find_project_config(Path(cwd))
    cfg.project_files = [str(x) for x in used]
    # only these keys are honoured from a PROJECT config
    for k in ("provider", "model", "approval", "agent", "theme", "max_tokens",
              "temperature", "top_p"):
        if k in merged and merged[k] is not None:
            setattr(cfg, k, merged[k])
    if isinstance(merged.get("instructions"), list):
        cfg.instructions = merged["instructions"]
    if isinstance(merged.get("permissions"), list):
        cfg.permissions = merged["permissions"]
    if isinstance(merged.get("agents"), dict):
        cfg.agents = merged["agents"]
    if isinstance(merged.get("mcp"), dict):
        cfg.mcp = merged["mcp"]


def _coerce(cfg: Config) -> None:
    if not isinstance(cfg.keys, dict):
        cfg.keys = {}
    if cfg.provider not in P.CATALOG:
        cfg.provider = P.DEFAULT_PROVIDER
    try:
        cfg.temperature = max(0.0, min(2.0, float(cfg.temperature)))
    except Exception:
        cfg.temperature = 0.3
    try:
        cfg.top_p = max(0.0, min(1.0, float(cfg.top_p)))
    except Exception:
        cfg.top_p = 0.95
    try:
        cfg.max_tokens = max(1024, int(cfg.max_tokens))
    except Exception:
        cfg.max_tokens = 16384
    try:
        cfg.max_steps = max(1, int(cfg.max_steps))
    except Exception:
        cfg.max_steps = 50
    if cfg.approval not in ("diff", "confirm", "yolo"):
        cfg.approval = "diff"


def save(cfg: Config) -> None:
    d = config_dir()
    d.mkdir(parents=True, exist_ok=True)
    data: Dict[str, Any] = {k: getattr(cfg, k) for k in _PERSISTED}
    p = config_path()
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2), "utf-8")
    for f in (tmp,):
        try:
            os.chmod(f, stat.S_IRUSR | stat.S_IWUSR)   # 0600
        except Exception:
            pass
    os.replace(tmp, p)
    try:
        os.chmod(p, stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        pass


def set_key(provider: str, key: str) -> Config:
    cfg = load()
    cfg.keys[provider] = (key or "").strip()
    save(cfg)
    return cfg
