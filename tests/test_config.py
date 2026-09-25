#!/usr/bin/env python3
"""test_config.py + providers — settings load/save/coerce, key resolution
(explicit → env), and catalog integrity."""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# isolate config to a temp dir
os.environ["XDG_CONFIG_HOME"] = tempfile.mkdtemp()
from priestcode import config as C, providers as P  # noqa: E402

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


print("== defaults ==")
cfg = C.load()
ck("default provider is deepseek", cfg.provider == "siliconflow")
ck("default model is V4.1-Flash",
   cfg.model_id() == "deepseek-ai/DeepSeek-V4.1-Flash", cfg.model_id())
ck("model is thinking_off (tuned)", cfg.model_obj().thinking_off)
ck("default approval is diff", cfg.approval == "diff")

print("\n== save / load round-trip ==")
cfg.provider = "openrouter"
cfg.model = ""
cfg.approval = "yolo"
cfg.keys["openrouter"] = "sk-or-test"
C.save(cfg)
cfg2 = C.load()
ck("provider persisted", cfg2.provider == "openrouter")
ck("approval persisted", cfg2.approval == "yolo")
ck("key persisted", cfg2.resolved_key() == "sk-or-test")
ck("openrouter default model is a free one",
   "free" in cfg2.model_id(), cfg2.model_id())

print("\n== config perms are 0600 (keys not world-readable) ==")
import stat  # noqa: E402
mode = stat.S_IMODE(os.stat(C.config_path()).st_mode)
ck("config is 0600", mode == 0o600, oct(mode))

print("\n== key from environment when not stored ==")
cfg3 = C.Config(provider="deepseek")
cfg3.keys = {}
os.environ["DEEPSEEK_API_KEY"] = "sk-env-123"
ck("env key resolved", cfg3.resolved_key() == "sk-env-123")
del os.environ["DEEPSEEK_API_KEY"]

print("\n== coercion of a hand-mangled config ==")
bad = C.Config(temperature="hot", max_tokens=-5, approval="chaos", top_p=9)
C._coerce(bad)
ck("temperature coerced", isinstance(bad.temperature, float))
ck("max_tokens floored", bad.max_tokens >= 1024)
ck("approval reset to diff", bad.approval == "diff")
ck("top_p clamped <=1", bad.top_p <= 1.0)

print("\n== provider catalog integrity ==")
ck("four providers", set(P.CATALOG) == {"siliconflow", "openrouter", "openai", "zen"})
for pid, prov in P.CATALOG.items():
    ck(f"{pid}: has models", len(prov.models) >= 1)
    ck(f"{pid}: base_url is https", prov.base_url.startswith("https://"))
    ck(f"{pid}: default model resolves", prov.default_model() is not None)
ck("openrouter has a free model", any(m.price == "free"
   for m in P.get_provider("openrouter").models))
ck("deepseek default is thinking_off",
   P.get_provider("siliconflow").default_model().thinking_off)

print("\n== zen serves free models with NO key (public token) ==")
_zen = P.get_provider("zen")
ck("zen needs no key", _zen.needs_key is False)
ck("zen carries a public token", _zen.public_token == "public")
_zcfg = C.Config(provider="zen")
_zcfg.keys = {}
ck("zen resolves the public token with no key set",
   _zcfg.resolved_key() == "public", _zcfg.resolved_key())
ck("zen counts as having a key (free, usable out of the box)", _zcfg.has_key())
ck("zen default is muse-spark free (the user's pick)",
   "muse-spark" in _zcfg.model_id(), _zcfg.model_id())
ck("a key-required provider with no key does NOT get a fake token",
   C.Config(provider="siliconflow", keys={}).resolved_key() == "")

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
