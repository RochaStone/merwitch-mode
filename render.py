"""Headless Chrome rendering for the wallpaper and the README images. Detects Chrome and says so kindly if missing."""
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

MAC = ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
       "/Applications/Chromium.app/Contents/MacOS/Chromium")
NO_CHROME = ("No Google Chrome or Chromium found, so no PNG this time. The SVG is ready: "
             "open it in your browser and take a screenshot, or install Chrome and run this again.")


def find_chrome():
    env = os.environ.get("CHROME")
    if env and os.path.isfile(env):
        return env
    for path in MAC:
        if os.path.isfile(path):
            return path
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    return None


def html_to_png(html_path, png_path, width, height):
    chrome = find_chrome()
    if not chrome:
        return False, NO_CHROME
    Path(png_path).parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as profile:
        try:
            subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--user-data-dir={profile}",
                            f"--window-size={width},{height}", "--virtual-time-budget=8000",
                            f"--screenshot={png_path}", Path(html_path).resolve().as_uri()],
                           capture_output=True, timeout=90)
        except (OSError, subprocess.SubprocessError) as exc:
            return False, f"Chrome could not render the picture ({exc})."
    if not os.path.isfile(png_path) or os.path.getsize(png_path) == 0:
        return False, "Chrome ran but wrote no picture."
    return True, f"PNG saved: {png_path} ({width}x{height})"


def svg_to_png(svg_path, png_path, width, height, ground):
    """Inline the SVG in a page (so its Google Fonts load); other screen shapes get margins in the ground colour."""
    svg = Path(svg_path).read_text(encoding="utf-8")
    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "wall.html"
        page.write_text(f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;background:{ground};'
                        f'overflow:hidden}}svg{{width:100vw;height:100vh;display:block}}</style>{svg}', encoding="utf-8")
        return html_to_png(page, png_path, width, height)
