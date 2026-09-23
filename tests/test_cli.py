#!/usr/bin/env python3
"""test_cli.py — argument parsing and the offline subcommands (version, models,
config) work without a network or a key."""
import io
import os
import sys
import tempfile
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ["XDG_CONFIG_HOME"] = tempfile.mkdtemp()
from priestcode import cli  # noqa: E402

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = cli.main(argv)
    return rc, buf.getvalue()


print("== --version ==")
rc, out = run(["--version"])
ck("rc 0", rc == 0)
ck("prints priest + version", "priest" in out and "." in out, out.strip())

print("\n== models ==")
rc, out = run(["models"])
ck("rc 0", rc == 0)
ck("lists deepseek + openrouter + openai",
   all(x in out for x in ("deepseek", "openrouter", "openai")), out[:80])
ck("shows the free tier", "free" in out)
ck("shows V4.1-Flash", "DeepSeek-V4.1-Flash" in out)

print("\n== config ==")
rc, out = run(["config"])
ck("rc 0", rc == 0)
ck("shows provider + model + approval",
   all(x in out for x in ("provider", "model", "approval")), out[:60])

print("\n== no key -> clean guidance, not a crash ==")
rc, out = run(["hello there"])   # no key configured in the temp home
ck("rc 2 (needs setup)", rc == 2, str(rc))
ck("points at auth", "auth" in out.lower(), out[:120])

print("\n== unknown provider -> clean error ==")
rc, out = run(["-P", "nonesuch", "hi"])
ck("rc 2", rc == 2)
ck("names the valid providers", "siliconflow" in out, out[:80])

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
