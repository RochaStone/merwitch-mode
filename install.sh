#!/usr/bin/env bash
# merwitch-mode installer. Makes Claude Code look and sound like a sacred tool.
#
#   ./install.sh                        the status line, the greeting, the thinking words and /merwitch
#   ./install.sh --motif cyberpunk      pick the look: analog, cyberpunk or y2k-blog (default: your style.json motif)
#   ./install.sh --chime on             turn the chime on (it starts off). --chime off turns it off again
#   ./install.sh --glyph sparkle        the leopard with sparkles, for terminals that show them (default: ascii)
#   ./install.sh --themes               also write your iTerm2, Ghostty and Warp themes and put them in place
#   ./install.sh --wallpaper [WxH]      render your wallpaper to ~/Pictures/merwitch.png (needs Google Chrome)
#   ./install.sh --uninstall            take it all back out, and bring back your old status line
#
# Your Claude Code settings are backed up before anything changes. Running it twice changes nothing.
# Changed your words in ~/.claude/merwitch-mode/words.json? Run ./install.sh again to pick them up.
set -euo pipefail
SRC="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="${CLAUDE_DIR:-$HOME/.claude}"
SETTINGS="$CLAUDE_DIR/settings.json"
HOME_DIR="$CLAUDE_DIR/merwitch-mode"
COMMAND="$CLAUDE_DIR/commands/merwitch.md"
MOTIF=""; CHIME=""; GLYPH=""; THEMES=0; WALL=""; UNINSTALL=0

ok()   { printf '\033[38;2;254;157;202m✧\033[0m %s\n' "$1"; }
fail() { printf '%s\n' "$1" >&2; exit 1; }

while [ $# -gt 0 ]; do
  case "$1" in
    --motif) MOTIF="${2:-}"; shift 2 ;;
    --chime) CHIME="${2:-}"; shift 2 ;;
    --glyph) GLYPH="${2:-}"; shift 2 ;;
    --themes) THEMES=1; shift ;;
    --wallpaper) WALL="2560x1600"; shift
                 if [[ "${1:-}" =~ ^[0-9]{3,5}x[0-9]{3,5}$ ]]; then WALL="$1"; shift; fi ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) fail "I don't know the option '$1'. Try ./install.sh --help" ;;
  esac
done
case "$MOTIF" in ""|analog|cyberpunk|y2k-blog) ;; *) fail "The motif is one of: analog, cyberpunk, y2k-blog" ;; esac
case "$CHIME" in ""|on|off) ;; *) fail "The chime is on or off" ;; esac
case "$GLYPH" in ""|ascii|sparkle) ;; *) fail "The glyph is ascii or sparkle" ;; esac
command -v python3 >/dev/null 2>&1 || fail "merwitch-mode needs python3. On a Mac, run: xcode-select --install"

if [ "$UNINSTALL" -eq 1 ]; then
  python3 "$SRC/scripts/merge_settings.py" uninstall --settings "$SETTINGS" --home "$HOME_DIR"
  if [ -f "$COMMAND" ] && grep -q "merwitch-mode" "$COMMAND"; then rm -f "$COMMAND"; ok "/merwitch removed"; fi
  if [ -d "$HOME_DIR" ]; then
    find "$HOME_DIR" -mindepth 1 -maxdepth 1 ! -name words.json -exec rm -rf {} +
    ok "merwitch-mode is out. Your words are kept in $HOME_DIR/words.json in case you come back."
  fi
  echo "Start a new Claude Code session to see your old look."
  exit 0
fi

# 1. Copy the parts Claude Code runs into ~/.claude/merwitch-mode, so this folder can move or update freely.
mkdir -p "$HOME_DIR/sounds" "$HOME_DIR/examples"
for f in statusline.py statusline.sh omen.py hooks.py merwitch_style.py; do cp "$SRC/$f" "$HOME_DIR/"; done
cp "$SRC/sounds/"*.wav "$HOME_DIR/sounds/"
cp "$SRC/examples/style.rocha-coded.json" "$HOME_DIR/examples/"
chmod +x "$HOME_DIR/statusline.sh"
[ -f "$HOME_DIR/words.json" ] || cp "$SRC/words.json" "$HOME_DIR/words.json"   # never overwrite your edits

# 2. Your choices, kept in config.json.
python3 - "$HOME_DIR/config.json" "$MOTIF" "$CHIME" "$GLYPH" <<'PY'
import json, sys
path, motif, chime, glyph = sys.argv[1:]
try:
    cfg = json.load(open(path, encoding="utf-8"))
    cfg = cfg if isinstance(cfg, dict) else {}
except (OSError, ValueError):
    cfg = {}
cfg.setdefault("motif", ""); cfg.setdefault("chime", False); cfg.setdefault("glyph", "ascii"); cfg.setdefault("pair", True)
if motif: cfg["motif"] = motif
if chime: cfg["chime"] = chime == "on"
if glyph: cfg["glyph"] = glyph
json.dump(cfg, open(path, "w", encoding="utf-8"), indent=2)
PY

# 3. The status line, three hooks and the thinking words, merged into settings.json with a backup.
python3 "$SRC/scripts/merge_settings.py" install --settings "$SETTINGS" --home "$HOME_DIR" --words "$HOME_DIR/words.json"

# 4. The /merwitch command: today's omen.
mkdir -p "$(dirname "$COMMAND")"
cat > "$COMMAND" <<MD
---
description: Draw today's omen (merwitch-mode)
allowed-tools: Bash(python3:*)
---
<!-- written by merwitch-mode/install.sh, removed by ./install.sh --uninstall -->
Today's omen:

!\`python3 "$HOME_DIR/omen.py"\`

Show the omen above to me exactly as printed, in a code block, and add nothing else.
MD
ok "/merwitch is ready"

if [ "$THEMES" -eq 1 ]; then
  TDIR="$HOME_DIR/themes"; mkdir -p "$TDIR"
  python3 "$SRC/themes/make-themes.py" --out "$TDIR"
  GH="${GHOSTTY_THEMES_DIR:-$HOME/.config/ghostty/themes}"; WARP="${WARP_THEMES_DIR:-$HOME/.warp/themes}"
  for f in "$TDIR"/*.ghostty; do mkdir -p "$GH"; cp "$f" "$GH/$(basename "$f" .ghostty)"; ok "Ghostty: add 'theme = $(basename "$f" .ghostty)' to ~/.config/ghostty/config"; done
  for f in "$TDIR"/*.yaml; do mkdir -p "$WARP"; cp "$f" "$WARP/"; ok "Warp: Settings > Appearance > Themes, then pick it"; done
  for f in "$TDIR"/*.itermcolors; do ok "iTerm2: double-click $f, then Settings > Profiles > Colors > Color Presets"; done
fi

if [ -n "$WALL" ]; then
  OUT="${WALLPAPER_OUT:-$HOME/Pictures/merwitch.png}"
  python3 "$SRC/make-wallpaper.py" ${MOTIF:+--motif "$MOTIF"} --out "$HOME_DIR/wallpaper.svg" --png "$OUT" --size "$WALL" \
    && ok "Set it: System Settings > Wallpaper > Add Photo, or right-click the file > Set Desktop Picture."
fi

[ "$CHIME" = "on" ] && ok "The chime is on. You will hear it when Claude finishes."
ok "Done. Start a new Claude Code session to see it."
