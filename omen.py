#!/usr/bin/env python3
"""The daily omen: one line, the same all day, a new one tomorrow.

  python3 omen.py                      today's omen, in your motif
  python3 omen.py --motif cyberpunk    analog | cyberpunk | y2k-blog
  python3 omen.py --date 2026-10-31    the omen for another day

The words come only from your style.json lines (Rocha's lines when the bundled example is in use)
and the neutral openers in words.json. The moon phase is worked out from the date.
"""
import argparse
import hashlib
import math
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import merwitch_style as ms  # noqa: E402

OMEN_KEYS = ("headline", "scrawl", "todo", "celebrate", "affirm")
PHASES = ("new moon", "waxing crescent", "first quarter", "waxing gibbous",
          "full moon", "waning gibbous", "last quarter", "waning crescent")
SYNODIC = 29.530588853
KNOWN_NEW = date(2000, 1, 6)   # a new moon, the usual reference point


def moon_phase(day):
    age = ((day - KNOWN_NEW).days + 0.5) % SYNODIC
    return PHASES[int(math.floor(age / SYNODIC * 8 + 0.5)) % 8]


def pick(items, day, salt):
    if not items:
        return ""
    n = int(hashlib.sha256(f"{day.isoformat()}:{salt}".encode()).hexdigest(), 16)
    return items[n % len(items)]


def omen_lines(style):
    lines = style.get("lines") or {}
    return [str(lines[k]).strip() for k in OMEN_KEYS if str(lines.get(k) or "").strip()]


def omen(style, words, day, motif):
    line = pick(omen_lines(style), day, "line")
    opener = pick(words.get("omen_openers") or [], day, "opener")
    moon = moon_phase(day)
    if line:
        body = f"{opener}: {line}" if opener else line
    else:
        body = pick(words.get("quiet") or [], day, "quiet") or ms.PLACEHOLDER
    stamp = day.strftime("%a %d %b").lower()
    if motif == "cyberpunk":
        return f"{ms.world(style)}:~$ omen --today\n> {moon} · {body}"
    if motif == "y2k-blog":
        return f"[merwitch.exe] mood: ✧ {moon} · {stamp}\n✧ {body}"
    return f"GUEST CHECK · {stamp} · {moon}\n✂┈ {body}"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--motif", default="")
    ap.add_argument("--style", default="")
    ap.add_argument("--date", default="")
    args = ap.parse_args()
    try:
        day = date.fromisoformat(args.date) if args.date else date.today()
    except ValueError:
        print("the date needs to look like 2026-10-31", file=sys.stderr)
        return 2
    style, _ = ms.load_style(args.style or None)
    cfg = ms.load_config()
    motif = ms.motif_of(args.motif or os.environ.get("MERWITCH_MOTIF") or cfg.get("motif") or style.get("motif"))
    print(omen(style, ms.load_words(), day, motif))
    return 0


if __name__ == "__main__":
    sys.exit(main())
