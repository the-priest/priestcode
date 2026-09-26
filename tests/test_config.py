#!/usr/bin/env python3
"""test_config.py + providers — settings load/save/coerce, key resolution
(explicit → env), and catalog integrity."""
import json
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
ck("providers include the free ones",
   {"siliconflow", "openrouter", "gemini", "groq", "zen", "openai"} <= set(P.CATALOG),
   str(sorted(P.CATALOG)))
for pid, prov in P.CATALOG.items():
    ck(f"{pid}: has models", len(prov.models) >= 1)
    ck(f"{pid}: base_url is https", prov.base_url.startswith("https://"))
    ck(f"{pid}: default model resolves", prov.default_model() is not None)
ck("openrouter has a free model", any(m.price == "free"
   for m in P.get_provider("openrouter").models))
ck("deepseek default is thinking_off",
   P.get_provider("siliconflow").default_model().thinking_off)

print("\n== free providers exist and are keyed (no fake keyless claims) ==")
_gem = P.get_provider("gemini")
ck("gemini is a free, no-card provider", any(m.price == "free" for m in _gem.models))
ck("gemini base is the OpenAI-compat endpoint",
   "generativelanguage.googleapis.com" in _gem.base_url and
   _gem.base_url.endswith("/openai"))
ck("gemini requires a key (honest)", _gem.needs_key is True)
ck("gemini uses the TEXT tool protocol (Gemini FC needs thought_signature)",
   _gem.native_tools is False)
ck("siliconflow keeps native function-calling",
   P.get_provider("siliconflow").native_tools is True)
_zen = P.get_provider("zen")
ck("zen requires a key (its free tier is OpenCode-app-only)", _zen.needs_key is True)
ck("zen sends no fake public token", not _zen.public_token)
ck("zen signup is honest about the OpenCode-only free tier",
   "opencode" in _zen.signup.lower() and "gemini" in _zen.signup.lower())
_zcfg = C.Config(provider="zen", keys={})
ck("zen with no key has_key() is False (so it prompts for one, not a raw error)",
   _zcfg.resolved_key() == "" and _zcfg.has_key() is False)

print("\n== priestcode reuses a key already set up in OpenCode ==")
_tmp = tempfile.mkdtemp()
os.environ["XDG_DATA_HOME"] = _tmp
_ocdir = os.path.join(_tmp, "opencode")
os.makedirs(_ocdir, exist_ok=True)
with open(os.path.join(_ocdir, "auth.json"), "w") as _fh:
    _fh.write(json.dumps({"opencode": {"type": "api", "key": "zen-abc-123"},
                          "google": {"type": "api", "key": "gem-xyz-789"}}))
ck("zen key is picked up from OpenCode's auth.json",
   C.opencode_key("zen") == "zen-abc-123", C.opencode_key("zen"))
ck("gemini key is picked up too", C.opencode_key("gemini") == "gem-xyz-789")
_zc = C.Config(provider="zen", keys={})
ck("a zen Config with no key resolves via OpenCode",
   _zc.resolved_key() == "zen-abc-123" and _zc.has_key())
del os.environ["XDG_DATA_HOME"]

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
