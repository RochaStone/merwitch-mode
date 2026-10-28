#!/usr/bin/env python3
"""merwitch-mode status line for Claude Code, in three motifs.

Claude Code pipes session JSON on stdin. This prints one line on a plum ground:
  analog     :(=^.^=): ✂┈ GUEST CHECK ┈ Opus ┈ ctx ●●●●○○○○○○ 42% ┈ $0.42 ┈ [ LORE ]
  cyberpunk  ░▒▓ :(=^.^=): rocheverse:~$ Opus · ctx ████░░░░░░ 42% · $0.42 · LORE ▓▒░ █
  y2k-blog   ▌merwitch.exe ■■■ ▌ :(=^.^=): mood ✧ Opus ┃ ctx ♥♥♥♥♡♡♡♡♡♡ 42% ┃ $0.42 ┃ visitor no. 000,007
Every part shows only when the data is there. Bad or empty input still prints a line.

Motif: $MERWITCH_MOTIF, then config.json motif, then style.json motif, then analog.
Glyph: the pixel leopard, ASCII by default. If pocket-familiar is hatched, her live sprite and mood
take the leopard's place (they pair). NO_COLOR=1 prints plain text.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import merwitch_style as ms  # noqa: E402

GLYPHS = {"ascii": ":(=^.^=):", "sparkle": "∴(=^･✧･^=)∴"}
STATE = os.path.join(ms.HERE, "state.json")


def rgb(h):
    h = h.lstrip("#")
    return ";".join(str(int(h[i:i + 2], 16)) for i in (0, 2, 4))


class Paint:
    def __init__(self, palette, on):
        self.p, self.on = palette, on

    def __call__(self, text, fg=None, bg=None, bold=False):
        if not self.on or not text:
            return text
        codes = (["1"] if bold else []) + ([f"38;2;{rgb(self.p[fg])}"] if fg else []) + \
                ([f"48;2;{rgb(self.p[bg])}"] if bg else [])
        return f"\033[{';'.join(codes)}m{text}\033[0m"


def read_input(raw):
    try:
        d = json.loads(raw) if raw.strip() else {}
    except ValueError:
        d = {}
    d = d if isinstance(d, dict) else {}

    def sub(key):
        v = d.get(key)
        return v if isinstance(v, dict) else {}
    model = sub("model").get("display_name") or sub("model").get("id") or ""
    cost = sub("cost").get("total_cost_usd")
    ctxw = sub("context_window")
    pct = ctxw.get("used_percentage")
    if not isinstance(pct, (int, float)) or isinstance(pct, bool):
        a, b = ctxw.get("total_input_tokens"), ctxw.get("context_window_size")
        pct = a * 100 / b if all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (a, b)) and b else None
    cwd = sub("workspace").get("current_dir") or d.get("cwd") or ""
    return {"model": str(model)[:30], "ctx": None if pct is None else max(0, min(100, round(pct))),
            "cost": f"${cost:.2f}" if isinstance(cost, (int, float)) and not isinstance(cost, bool) and cost > 0 else "",
            "cwd": cwd if isinstance(cwd, str) else ""}


def visitors():
    n = ms.read_json(os.environ.get("MERWITCH_STATE") or STATE).get("visitors")
    return n if isinstance(n, int) and n >= 0 else 0


def familiar_sprite(cfg):
    """pocket-familiar's live sprite, name and mood, when she is installed and hatched."""
    if not cfg.get("pair", True) or os.environ.get("MERWITCH_PAIR") == "0":
        return ""
    exe = os.environ.get("MERWITCH_FAMILIAR") or os.path.expanduser("~/.claude/skills/pocket-familiar/familiar")
    if not os.path.isfile(exe):
        return ""
    try:
        out = subprocess.run([sys.executable, exe, "line"], input="", capture_output=True, text=True, timeout=1.5,
                             env={**os.environ, "NO_COLOR": "1"}).stdout
    except (OSError, subprocess.SubprocessError):
        return ""
    head = out.strip().split(" · ")[0].strip()
    return "" if not head or "an egg" in head else " ".join(head.split())


def bar(ctx, full, empty):
    n = min(10, max(0, (ctx + 5) // 10))
    return full * n + empty * (10 - n)


def build(info, style, motif, cfg, on=True):
    p = style["palette"]
    paint = Paint(p, on)
    stamp = str((style.get("lines") or {}).get("stamp") or "").strip()
    glyph = familiar_sprite(cfg) or GLYPHS.get(cfg.get("glyph"), GLYPHS["ascii"])
    low = info["ctx"] is not None and info["ctx"] >= 80
    if motif == "cyberpunk":
        parts = [x for x in (info["model"], info["ctx"] is not None and f"ctx {bar(info['ctx'], '█', '░')} {info['ctx']}%",
                             info["cost"], stamp) if x]
        if not on:
            return f"{glyph} {ms.world(style)}:~$ " + " · ".join(parts)
        type_ = "gold" if low else "paper"
        return (paint("░▒", "wine") + paint("▓", "hero") + paint(" ", bg="hero") + paint(glyph, "accent", "hero", True)
                + paint(f" {ms.world(style)}:~$ ", "gold", "hero") + paint(" · ".join(parts) + " ", type_, "hero")
                + paint("▓", "hero") + paint("▒░", "wine") + " " + paint("█", "accent"))
    if motif == "y2k-blog":
        parts = [x for x in ("mood ✧", info["model"], info["ctx"] is not None and f"ctx {bar(info['ctx'], '♥', '♡')} {info['ctx']}%",
                             info["cost"], f"visitor no. {visitors():07,d}") if x]
        if not on:
            return f"[merwitch.exe] {glyph} " + " | ".join(parts)
        return (paint(" merwitch.exe ", "paper", "hero", True) + paint("■■■ ", "gold", "hero")
                + paint(" ", bg="paper") + paint(glyph, "marker", "paper", True)
                + paint(" " + " ┃ ".join(parts) + " ", "wine" if low else "ink", "paper"))
    # analog: a guest check torn from the pad
    parts = [x for x in (info["model"], info["ctx"] is not None and f"ctx {bar(info['ctx'], '●', '○')} {info['ctx']}%",
                         info["cost"]) if x]
    if not on:
        return f"{glyph} GUEST CHECK " + " ┈ ".join(parts) + (f" [ {stamp} ]" if stamp else "")
    return (paint(" ", bg="hero") + paint(glyph, "accent", "hero", True) + paint(" ", bg="hero")
            + paint(" ✂┈ GUEST CHECK ┈ ", "wine", "paper_pink", True)
            + paint(" ┈ ".join(parts) + " ", "marker" if low else "ink", "paper_pink")
            + (paint(f" {stamp} ", "paper_pink", "wine", True) if stamp else ""))


def main():
    raw = "" if sys.stdin.isatty() else sys.stdin.read()
    info = read_input(raw)
    cfg = ms.load_config()
    style, _ = ms.load_style(cwd=info["cwd"] or None)
    motif = ms.motif_of(os.environ.get("MERWITCH_MOTIF") or cfg.get("motif") or style.get("motif"))
    print(build(info, style, motif, cfg, on=not os.environ.get("NO_COLOR")))


if __name__ == "__main__":
    try:
        main()
    except Exception:  # the status bar must never go blank
        print(GLYPHS["ascii"])
