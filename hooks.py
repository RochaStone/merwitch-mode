#!/usr/bin/env python3
"""Claude Code hooks for merwitch-mode. Quiet, quick, and always exit 0 so they never block Claude.

  hooks.py greet    SessionStart: counts the visit, shows a greeting and today's omen
  hooks.py done     Stop: plays the chime, if the chime is on
  hooks.py notify   Notification: plays the softer bell, if the chime is on

The chime is off until you turn it on: ./install.sh --chime on
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import merwitch_style as ms  # noqa: E402
import omen as om  # noqa: E402
from statusline import GLYPHS, STATE  # noqa: E402

SOUNDS = {"done": "chime.wav", "notify": "bell.wav"}


def read_event():
    raw = "" if sys.stdin.isatty() else sys.stdin.read()
    try:
        d = json.loads(raw) if raw.strip() else {}
    except ValueError:
        d = {}
    return d if isinstance(d, dict) else {}


def count_visit(source):
    path = os.environ.get("MERWITCH_STATE") or STATE
    state = ms.read_json(path)
    if source in ("", "startup", "clear"):
        n = state.get("visitors")
        state["visitors"] = (n if isinstance(n, int) and n >= 0 else 0) + 1
        fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path) or ".", prefix=".state-")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(state, fh)
        os.replace(tmp, path)


def greet(event):
    try:
        count_visit(str(event.get("source") or ""))
    except OSError:
        pass   # a read-only folder only means the counter stays still
    style, _ = ms.load_style(cwd=event.get("cwd") if isinstance(event.get("cwd"), str) else None)
    words, today = ms.load_words(), date.today()
    hello = om.pick(words.get("greeting") or [], today, "greeting")
    line = om.pick(om.omen_lines(style), today, "line")
    text = " · ".join(x for x in (hello, line) if x)
    print(json.dumps({"systemMessage": f"{GLYPHS['ascii']} {text}".strip()}, ensure_ascii=False))


def player():
    forced = os.environ.get("MERWITCH_PLAYER")
    if forced:
        return [forced]
    for name, args in (("afplay", []), ("paplay", []), ("aplay", ["-q"])):
        exe = shutil.which(name)
        if exe:
            return [exe] + args
    return []


def chime(kind):
    if not ms.load_config().get("chime"):
        return
    wav = os.path.join(ms.HERE, "sounds", SOUNDS[kind])
    cmd = player()
    if cmd and os.path.isfile(wav):
        subprocess.Popen(cmd + [wav], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else ""
    event = read_event()
    if kind == "greet":
        greet(event)
    elif kind in SOUNDS:
        chime(kind)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # a hook must never block Claude; say why on stderr only
        print(f"merwitch-mode: {exc}", file=sys.stderr)
    sys.exit(0)
