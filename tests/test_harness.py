#!/usr/bin/env python3
"""test_harness.py — the tool-call canonicaliser, including DeepSeek's degraded
native syntax (the bug that made a whole family of models look broken)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from priestcode import harness as H  # noqa: E402

_p = _f = 0


def ck(name, cond, detail=""):
    global _p, _f
    if cond:
        _p += 1
        print(f"  PASS {name}")
    else:
        _f += 1
        print(f"  FAIL {name}" + (f"   [{detail}]" if detail else ""))


FW = "｜"
SEP = "▁"


def ds(pipe, sep, name="read_file", body='{"path": "a.py"}'):
    return (f"<{pipe}tool{sep}calls{sep}begin{pipe}>"
            f"<{pipe}tool{sep}call{sep}begin{pipe}>function"
            f"<{pipe}tool{sep}sep{pipe}>{name}\n```json\n{body}\n```"
            f"<{pipe}tool{sep}call{sep}end{pipe}>"
            f"<{pipe}tool{sep}calls{sep}end{pipe}>")


print("== canonical dialects parse ==")
CASES = {
    "canonical tool tag": '<tool name="read_file">{"path": "a.py"}</tool>',
    "deepseek native": ds(FW, SEP),
    "tool_call tag": '<tool_call name="read_file">{"path": "a.py"}</tool_call>',
    "invoke tag": '<invoke name="read_file">{"path": "a.py"}</invoke>',
    "function=name": '<function=read_file>{"path": "a.py"}</function>',
    "invoke+parameter": ('<invoke name="read_file"><parameter name="path">'
                         'a.py</parameter></invoke>'),
}
for label, raw in CASES.items():
    c = H.parse_tool_calls(raw)
    ck(f"{label}: one call", len(c) == 1, str(len(c)))
    if c:
        ck(f"{label}: name+arg", c[0].name == "read_file"
           and c[0].args.get("path") == "a.py", f"{c[0].name} {c[0].args}")

print("\n== degraded pipes/separators still parse (the empty-loop bug) ==")
for label, p, s in [("ascii | + underscore", "|", "_"),
                    ("ascii | + block", "|", SEP),
                    ("box | + block", "│", SEP),
                    ("doubled || + underscore", "||", "_"),
                    ("fullwidth + underscore", FW, "_")]:
    c = H.parse_tool_calls(ds(p, s))
    ck(f"{label}: parses to one call", len(c) == 1 and c[0].name == "read_file",
       str(c))
    disp = H.clean_reply(ds(p, s))
    ck(f"{label}: strips clean (no raw tokens on screen)", disp == "", repr(disp))

print("\n== prose is never mistaken for a call ==")
for prose in ("use the <tool> element in html",
              "a < b and c > d in function=x",
              "pipe a <|b|> c in a table",
              "regex <|foo|> here",
              "plain text no brackets"):
    ck(f"no call from: {prose[:30]!r}", len(H.parse_tool_calls(prose)) == 0,
       str(H.parse_tool_calls(prose)))

print("\n== multiple calls, and mixed prose+call ==")
two = ds(FW, SEP, "read_file", '{"path":"a"}') + "\n" + \
    ds(FW, SEP, "read_file", '{"path":"b"}')
ck("two native calls both parse", len(H.parse_tool_calls(two)) == 2)
mixed = "I'll read it.\n" + ds("|", "_")
mc = H.parse_tool_calls(mixed)
ck("prose+degraded call: call recovered", len(mc) == 1)
ck("prose+degraded call: prose survives strip",
   "read it" in H.clean_reply(mixed))

print("\n== empty <calls></calls> wrapper is scrubbed ==")
ck("empty wrapper -> no call", len(H.parse_tool_calls("<calls></calls>")) == 0)
ck("empty wrapper -> empty display", H.clean_reply("<calls></calls>") == "")

print("\n== bad JSON body is flagged, not crashed ==")
bad = H.parse_tool_calls('<tool name="run">{not json}</tool>')
ck("bad json -> one raw call", len(bad) == 1 and bad[0].raw)

print("\n== idempotent ==")
ck("canonicalise twice == once",
   H.canonicalise(H.canonicalise(ds(FW, SEP))) == H.canonicalise(ds(FW, SEP)))

print(f"\n{_p} passed, {_f} failed")
sys.exit(1 if _f else 0)
