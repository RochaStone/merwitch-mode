"""Finds and loads the shared style.json, and the merwitch words and settings.

Style lookup order: $ROCHA_CODED_STYLE, ./style.json (or <cwd>/style.json), ~/.rocha-coded/style.json,
then the bundled example (Rocha's look).
Inheritance rule: when a user style.json exists, ONLY missing palette colours and fonts fall back to the
bundled example. Lines, owner, handle, name, references and notes never fall back to hers.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
BUNDLED = os.path.join(HERE, "examples", "style.rocha-coded.json")
WORDS = os.path.join(HERE, "words.json")
CONFIG = os.path.join(HERE, "config.json")
HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")
INHERITED = ("palette", "fonts")
MOTIFS = ("analog", "cyberpunk", "y2k-blog")
MOTIF_ALIASES = {"guest-check": "analog", "front-page": "analog", "magazine-scrawl": "analog", "pink-paper": "analog",
                 "neutral": "analog", "retro-tv": "cyberpunk", "leopard": "cyberpunk", "rotary": "y2k-blog",
                 "sticker-collage": "y2k-blog", "y2k": "y2k-blog"}
PIXEL_FONT = "Silkscreen"
PLACEHOLDER = "YOUR WORDS HERE"
FALLBACK = {"hero": "#50163C", "accent": "#FE9DCA", "paper": "#FFF7F4", "paper_pink": "#FFE3F1", "ink": "#3B1230",
            "marker": "#C2246E", "plum": "#50163C", "wine": "#682047", "gold": "#E9B949", "cool": "#B9B3F5"}
DEFAULT_CONFIG = {"motif": "", "chime": False, "glyph": "ascii", "pair": True}


def read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def find_style(cwd=None):
    candidates = [os.environ.get("ROCHA_CODED_STYLE", ""),
                  os.path.join(cwd or os.getcwd(), "style.json"),
                  os.path.expanduser("~/.rocha-coded/style.json"), BUNDLED]
    for path in candidates:
        if path and os.path.isfile(path):
            return os.path.abspath(path)
    return ""


def _merge(base, over):
    out = dict(base)
    for key, val in over.items():
        if isinstance(val, dict) and isinstance(base.get(key), dict):
            out[key] = _merge(base[key], val)
        elif val not in ("", None, [], {}):
            out[key] = val
    return out


def is_bundled(path):
    return not path or os.path.abspath(path) == os.path.abspath(BUNDLED)


def load_style(path=None, cwd=None):
    """Returns (style, path used). Bad hex colours fall back to the bundled ones."""
    base = read_json(BUNDLED)
    path = path or find_style(cwd)
    if is_bundled(path):
        style = json.loads(json.dumps(base))
    else:
        user = read_json(path)
        style = {k: v for k, v in user.items() if k not in INHERITED}
        for key in INHERITED:
            style[key] = _merge(base.get(key, {}), user.get(key) if isinstance(user.get(key), dict) else {})
    if not isinstance(style.get("lines"), dict):
        style["lines"] = {}
    palette = style.setdefault("palette", {})
    for key in FALLBACK:
        val = palette.get(key)
        if not (isinstance(val, str) and HEX.match(val)):
            good = base.get("palette", {}).get(key, "")
            palette[key] = good if HEX.match(str(good)) else FALLBACK[key]
    return style, path


def motif_of(value):
    """analog, cyberpunk or y2k-blog for any motif value. Unknown or blank means analog."""
    v = str(value or "").strip().lower()
    return v if v in MOTIFS else MOTIF_ALIASES.get(v, "analog")


def slug(name):
    s = re.sub(r"[^a-z0-9]+", "-", str(name).lower()).strip("-")
    return s or "my-style"


def world(style):
    """The prompt name: lines.magazine, else the style's name. Never borrowed from the example."""
    raw = (style.get("lines") or {}).get("magazine") or style.get("name") or ""
    return slug(raw) if raw else "my-world"


def load_words(path=None):
    data = read_json(path or os.environ.get("MERWITCH_WORDS") or WORDS)
    out = {}
    for key in ("thinking", "greeting", "omen_openers", "quiet"):
        val = data.get(key)
        out[key] = [str(x).strip() for x in val if str(x).strip()] if isinstance(val, list) else []
    return out


def load_config(path=None):
    cfg = dict(DEFAULT_CONFIG)
    cfg.update({k: v for k, v in read_json(path or os.environ.get("MERWITCH_CONFIG") or CONFIG).items()
                if k in DEFAULT_CONFIG})
    return cfg
