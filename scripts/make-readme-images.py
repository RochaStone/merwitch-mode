#!/usr/bin/env python3
"""Generates every image the README uses, from the tool itself. Needs Chrome or Chromium for the PNGs.

  python3 scripts/make-readme-images.py

The status lines in the pictures are the real output of statusline.py, turned from terminal colour codes
into HTML. The omen is the real output of omen.py. Writes:
  docs/img/hero-y2k.png        a y2k-blog window called merwitch.exe: a Claude Code session with the
                               greeting, /merwitch and its omen, a thinking word and the plum status line
  docs/img/triptych.png        analog | cyberpunk | y2k-blog: the wallpaper and the status line in each
  docs/img/step-01..05.svg     pixel step badges, docs/img/divider.svg, docs/img/heart.svg
  docs/IMAGES.md               the list of all of the above
"""
import html
import json
import os
import re
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import importlib.util  # noqa: E402

import merwitch_style as ms  # noqa: E402
import omen as om  # noqa: E402
import render  # noqa: E402
import statusline as sl  # noqa: E402

spec = importlib.util.spec_from_file_location("wallpaper", ROOT / "make-wallpaper.py")
wallpaper = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wallpaper)

IMG = ROOT / "docs" / "img"
DAY = date(2026, 10, 31)
SAMPLE = {"model": {"display_name": "Opus"}, "cost": {"total_cost_usd": 0.42}, "context_window": {"used_percentage": 42}}
DIGITS = {"0": ["111", "101", "101", "101", "111"], "1": ["010", "110", "010", "010", "111"],
          "2": ["111", "001", "111", "100", "111"], "3": ["111", "001", "111", "001", "111"],
          "4": ["101", "101", "111", "001", "001"], "5": ["111", "100", "111", "001", "111"]}
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,900'
         '&family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,800&family=DM+Mono:wght@400;500&family=Silkscreen'
         '&display=block">')


def pix(text, x0, y0):
    return "".join(f"M{x0 + n * 4 + c} {y0 + r}h1v1h-1z" for n, ch in enumerate(text)
                   for r, row in enumerate(DIGITS[ch]) for c, bit in enumerate(row) if bit == "1")


def badge(num, ground, gold):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 11 9" width="33" height="27" shape-rendering="crispEdges">'
            f'<path fill="{ground}" d="M1 0h9v1h1v7h-1v1H1v-1H0V1h1z"/><path fill="{gold}" d="{pix(num, 2, 2)}"/></svg>\n')


def divider(gold):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="720" height="6" shape-rendering="crispEdges"><defs>'
            '<pattern id="p" width="12" height="6" patternUnits="userSpaceOnUse">'
            f'<rect width="6" height="2" y="2" fill="{gold}"/><rect x="8" y="2" width="2" height="2" fill="{gold}"/>'
            '</pattern></defs><rect width="720" height="6" fill="url(#p)"/></svg>\n')


def heart(colour):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 7 6" width="21" height="18" shape-rendering="crispEdges">'
            f'<path fill="{colour}" d="M1 0h2v1h1V0h2v1h1v2H6v1H5v1H4v1H3V5H2V4H1V3H0V1h1z"/></svg>\n')


def ansi_to_html(text):
    """Truecolour SGR codes to spans. Only the codes statusline.py writes: 0, 1, 38;2;r;g;b, 48;2;r;g;b."""
    out, pos = [], 0
    for m in re.finditer(r"\033\[([0-9;]*)m", text):
        out.append(html.escape(text[pos:m.start()]))
        pos = m.end()
        codes = [int(c) for c in m.group(1).split(";") if c]
        if codes in ([], [0]):
            out.append("</span>")
            continue
        css, i = [], 0
        while i < len(codes):
            if codes[i] == 1:
                css.append("font-weight:500")
                i += 1
            elif codes[i] in (38, 48) and i + 4 < len(codes) + 1:
                prop = "color" if codes[i] == 38 else "background"
                css.append(f"{prop}:rgb({codes[i + 2]},{codes[i + 3]},{codes[i + 4]})")
                i += 5
            else:
                i += 1
        out.append(f'<span style="{";".join(css)}">')
    out.append(html.escape(text[pos:]))
    return "".join(out)


def status(style, motif, on=True):
    cfg = dict(ms.DEFAULT_CONFIG, pair=False)
    os.environ["MERWITCH_STATE"] = str(STATE)
    return sl.build(sl.read_input(json.dumps(SAMPLE)), style, motif, cfg, on=on)


def hero_html(style, words):
    p = style["palette"]
    line = ansi_to_html(status(style, "cyberpunk"))
    greet = f'{sl.GLYPHS["ascii"]} {om.pick(words["greeting"], DAY, "greeting")} · {om.pick(om.omen_lines(style), DAY, "line")}'
    omen = html.escape(om.omen(style, words, DAY, "y2k-blog"))
    thinking = words["thinking"][1] if len(words["thinking"]) > 1 else "Casting"
    owner = html.escape(str(style.get("owner") or "").lower()) or "&#160;"
    return f"""<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>
* {{ margin:0; box-sizing:border-box; }}
body {{ width:1200px; height:620px; padding:40px 48px; font-family:"Bricolage Grotesque",sans-serif; color:{p['ink']};
  background:{p['paper_pink']} url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' shape-rendering='crispEdges'%3E%3Cpath fill='{p['accent'].replace('#', '%23')}' d='M25 24h4v2h2v-2h4v2h2v4h-2v2h-2v2h-2v2h-2v-2h-2v-2h-2v-2h-2v-4h2z'/%3E%3C/svg%3E"); }}
.win {{ background:{p['paper']}; border:4px solid {p['hero']}; box-shadow:0 18px 30px rgba(0,0,0,.25); height:100%; display:flex; flex-direction:column; }}
.bar {{ background:{p['hero']}; color:{p['paper']}; font-family:Silkscreen,monospace; font-size:20px; padding:10px 16px; display:flex; justify-content:space-between; }}
.bar i {{ display:inline-block; width:22px; height:20px; background:{p['gold']}; border:2px solid {p['ink']}; margin-left:8px; }}
.body {{ display:flex; gap:22px; padding:22px; flex:1; min-height:0; }}
.term {{ flex:1; background:{p['ink']}; color:{p['paper']}; font-family:"DM Mono",monospace; font-size:16px; line-height:1.55;
  padding:18px 18px 14px; display:flex; flex-direction:column; border:3px solid {p['wine']}; }}
.term pre {{ font-family:inherit; white-space:pre-wrap; }}
.dim {{ color:{p['accent']}; }} .gold {{ color:{p['gold']}; }} .spin {{ color:{p['accent']}; margin-top:12px; }}
.omen {{ border:1px dashed {p['gold']}; padding:10px 12px; margin:8px 0; }}
.status {{ margin-top:auto; white-space:pre; font-size:15px; }}
aside {{ width:250px; display:flex; flex-direction:column; gap:14px; }}
.box {{ border:3px solid {p['hero']}; background:{p['paper_pink']}; }}
.box h3 {{ background:{p['hero']}; color:{p['paper']}; font:400 14px Silkscreen,monospace; padding:6px 10px; }}
.box p {{ padding:10px 12px; font-weight:800; font-size:18px; }}
.count {{ font-family:"DM Mono",monospace; font-size:15px; }}
h1 {{ font-family:Fraunces,serif; font-weight:900; font-size:30px; color:{p['wine']}; margin:2px 0 4px; }}
</style></head><body><div class="win">
<div class="bar"><span>merwitch.exe</span><span><i></i><i></i><i></i></span></div>
<div class="body"><div class="term">
<pre class="dim">{html.escape(greet)}</pre>
<pre><span class="gold">&gt;</span> /merwitch</pre>
<pre class="omen">{omen}</pre>
<pre><span class="gold">&gt;</span> write this week's newsletter</pre>
<pre class="spin">✻ {html.escape(thinking)}…</pre>
<pre class="status">{line}</pre>
</div><aside>
<h1>merwitch mode</h1>
<div class="box"><h3>about me</h3><p>{owner}</p></div>
<div class="box"><h3>mood</h3><p>✧ {html.escape(om.moon_phase(DAY))}</p></div>
<div class="box"><h3>guestbook</h3><p>sign my guestbook ✧</p></div>
<div class="count">you are visitor no. 000,777</div>
<div class="count">last updated {DAY.strftime('%d %b %Y').lower()}</div>
</aside></div></div></body></html>"""


def triptych_html(style, walls):
    p = style["palette"]
    cells = ""
    for motif, svg in walls.items():
        svg = re.sub(r'width="\d+" height="\d+"', 'width="100%" height="100%"', svg, count=1)
        cells += (f'<figure><div class="wall">{svg}</div><pre class="term">{ansi_to_html(status(style, motif))}</pre>'
                  f'<figcaption>{motif}</figcaption></figure>')
    return f"""<!doctype html><html><head><meta charset="utf-8">{FONTS}<style>
* {{ margin:0; box-sizing:border-box; }}
body {{ width:1620px; height:480px; background:{p['hero']}; display:flex; gap:26px; padding:26px 30px; }}
figure {{ flex:1; display:flex; flex-direction:column; gap:12px; min-width:0; }}
.wall {{ aspect-ratio:16/10; border:2px solid {p['gold']}; overflow:hidden; }}
.wall svg {{ display:block; }}
.term {{ background:{p['ink']}; border:2px solid {p['gold']}; padding:10px 10px; font:11.5px/1.9 "DM Mono",monospace; white-space:pre-wrap; overflow:hidden; height:62px; }}
figcaption {{ font-family:Silkscreen,monospace; color:{p['paper']}; font-size:22px; text-align:center; }}
</style></head><body>{cells}</body></html>"""


def main():
    global STATE
    style, _ = ms.load_style(str(ms.BUNDLED))
    words = ms.load_words(str(ROOT / "words.json"))
    p = style["palette"]
    IMG.mkdir(parents=True, exist_ok=True)
    for i in range(1, 6):
        (IMG / f"step-{i:02d}.svg").write_text(badge(f"{i:02d}", p["hero"], p["gold"]), encoding="utf-8")
    (IMG / "divider.svg").write_text(divider(p["gold"]), encoding="utf-8")
    (IMG / "heart.svg").write_text(heart(p["accent"]), encoding="utf-8")
    print("SVGs: step-01..05, divider, heart")
    ok_all = True
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        STATE = tmp / "state.json"
        STATE.write_text('{"visitors": 777}', encoding="utf-8")   # the demo counter in the pictures
        hero = tmp / "hero.html"
        hero.write_text(hero_html(style, words), encoding="utf-8")
        ok, msg = render.html_to_png(hero, IMG / "hero-y2k.png", 1200, 620)
        print(msg)
        ok_all &= ok
        walls = {m: wallpaper.build(style, m, DAY.strftime("%d %b %Y")) for m in ms.MOTIFS}
        strip = tmp / "triptych.html"
        strip.write_text(triptych_html(style, walls), encoding="utf-8")
        ok, msg = render.html_to_png(strip, IMG / "triptych.png", 1620, 480)
        print(msg)
        ok_all &= ok
    (ROOT / "docs" / "IMAGES.md").write_text("""# Images

Every image here is generated by `scripts/make-readme-images.py` from the tool itself: the status lines are the
real output of `statusline.py`, the omen is the real output of `omen.py`, and the wallpapers come from
`make-wallpaper.py`. No photos, no real people, no faces. The visitor number 000,777 in the pictures is a demo value.

| File | What it is |
|---|---|
| `docs/img/hero-y2k.png` | a y2k-blog window titled merwitch.exe with a Claude Code session inside: the greeting, /merwitch and its omen, a thinking word and the plum status line |
| `docs/img/triptych.png` | analog, cyberpunk and y2k-blog side by side: the wallpaper and the status line in each |
| `docs/img/step-01.svg` to `step-05.svg` | pixel step badges for "Start here" |
| `docs/img/divider.svg` | a gold pixel hairline between README sections |
| `docs/img/heart.svg` | the pixel heart beside "If it goes wrong" |
| `sounds/chime.wav`, `sounds/bell.wav` | the two sounds, generated from sine waves by `scripts/make-chime.py` (not images, listed so every made thing is accounted for) |
| `themes/rocha-coded.*` | the terminal themes, generated by `themes/make-themes.py` from the bundled style |
""", encoding="utf-8")
    print("docs/IMAGES.md written" + ("" if ok_all else " (some PNGs skipped)"))
    return 0 if ok_all else 1


STATE = Path(os.devnull)

if __name__ == "__main__":
    sys.exit(main())
