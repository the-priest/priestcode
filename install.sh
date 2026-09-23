#!/usr/bin/env bash
# Priest Code installer.
#
#   curl -fsSL https://raw.githubusercontent.com/the-priest/priestcode/main/install.sh | bash
#
# Works on Arch/CachyOS, Debian/Kali/Ubuntu, Fedora and macOS. Modern distros
# mark the system Python "externally managed" (PEP 668), so a plain
# "pip install --user" is refused. This installs Priest Code into its OWN
# virtual environment and links the "priest" command into ~/.local/bin. The
# system Python is never touched.
#
#   bash install.sh --uninstall     remove it again

set -euo pipefail

REPO="the-priest/priestcode"
TARBALL="https://github.com/${REPO}/archive/refs/heads/main.tar.gz"
PREFIX="${PRIESTCODE_HOME:-$HOME/.local/share/priestcode}"
VENV="$PREFIX/venv"
BIN="$HOME/.local/bin"

say()  { printf '  %s\n' "$*"; }
die()  { printf 'error: %s\n' "$*" >&2; exit 1; }

if [ "${1:-}" = "--uninstall" ]; then
  rm -rf "$PREFIX"
  rm -f "$BIN/priest" "$BIN/priestcode"
  say "removed Priest Code."
  exit 0
fi

printf '\n  Priest Code installer\n\n'

# 1. Python
PY="$(command -v python3 || true)"
[ -n "$PY" ] || die "python3 not found. Install Python 3.9+ and re-run."
VER="$("$PY" -c 'import sys;print("%d.%d"%sys.version_info[:2])')"
say "using python $VER at $PY"
"$PY" - <<'PYEOF' || die "Python 3.9 or newer is required."
import sys; sys.exit(0 if sys.version_info[:2] >= (3, 9) else 1)
PYEOF

# 2. Fetch the source into a temp dir (unless we are already in a checkout)
SRC=""
if [ -f "pyproject.toml" ] && grep -q 'name = "priestcode"' pyproject.toml 2>/dev/null; then
  SRC="$(pwd)"
  say "installing from the current checkout"
else
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  say "downloading priestcode…"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$TARBALL" | tar -xz -C "$TMP"
  elif command -v wget >/dev/null 2>&1; then
    wget -qO- "$TARBALL" | tar -xz -C "$TMP"
  else
    die "need curl or wget to download."
  fi
  SRC="$(find "$TMP" -maxdepth 1 -type d -name 'priestcode-*' | head -n1)"
  [ -n "$SRC" ] || die "download looked wrong (no source dir)."
fi

# 3. Build an isolated virtualenv and install into it
say "creating a private virtual environment…"
rm -rf "$VENV"
"$PY" -m venv "$VENV" || die "could not create a venv (install python3-venv?)."
"$VENV/bin/python" -m pip install --quiet --upgrade pip >/dev/null 2>&1 || true
say "installing (this pulls textual + rich)…"
"$VENV/bin/python" -m pip install --quiet "$SRC" || die "pip install failed."

# 4. Link the command onto the PATH
mkdir -p "$BIN"
ln -sf "$VENV/bin/priest" "$BIN/priest"
ln -sf "$VENV/bin/priest" "$BIN/priestcode"
say "linked 'priest' into $BIN"

printf '\n  Done.\n\n'
case ":$PATH:" in
  *":$BIN:"*) : ;;
  *) printf '  NOTE: %s is not on your PATH. Add this to your shell rc:\n' "$BIN"
     printf '        export PATH="%s:$PATH"\n\n' "$BIN" ;;
esac
printf '  Next:\n'
printf '    priest auth     # pick a provider and paste a key\n'
printf '    priest          # launch in the current repo\n\n'
