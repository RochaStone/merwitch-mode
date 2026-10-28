"""merwitch-mode tests. Run from the repo root: python3 -m unittest discover -s tests -v"""
import json
import os
import plistlib
import shutil
import subprocess
import sys
import tempfile
import unittest
import wave
import xml.dom.minidom
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import merwitch_style as ms  # noqa: E402
import omen as om  # noqa: E402
import statusline as sl  # noqa: E402

BUNDLED = str(ROOT / "examples" / "style.rocha-coded.json")
SAMPLE = '{"model":{"display_name":"Opus"},"cost":{"total_cost_usd":0.4213},"context_window":{"used_percentage":42.4}}'
HER_WORDS = ("LORE", "rocheverse", "FOUNDER WORLD", "founder world", "I AM SO LUCKY", "EVERYTHING WORKS OUT")


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="merwitch-test-"))
        self.env = {**os.environ, "ROCHA_CODED_STYLE": BUNDLED, "MERWITCH_PAIR": "0",
                    "MERWITCH_CONFIG": str(self.tmp / "config.json"), "MERWITCH_STATE": str(self.tmp / "state.json")}
        self.env.pop("NO_COLOR", None)
        self.env.pop("MERWITCH_MOTIF", None)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_py(self, script, *args, stdin="", **env):
        return subprocess.run([sys.executable, str(ROOT / script), *args], input=stdin, capture_output=True,
                              text=True, env={**self.env, **env}, cwd=self.tmp, timeout=60)

    def line(self, stdin=SAMPLE, **env):
        return subprocess.run(["bash", str(ROOT / "statusline.sh")], input=stdin, capture_output=True, text=True,
                              env={**self.env, **env}, cwd=self.tmp, timeout=30).stdout.rstrip("\n")

    def write(self, name, data):
        path = self.tmp / name
        path.write_text(json.dumps(data) if not isinstance(data, str) else data, encoding="utf-8")
        return str(path)


class StatusLine(Base):
    def test_three_motifs_plain(self):
        self.assertEqual(self.line(NO_COLOR="1", MERWITCH_MOTIF="analog"),
                         ":(=^.^=): GUEST CHECK Opus ┈ ctx ●●●●○○○○○○ 42% ┈ $0.42 [ LORE ]")
        self.assertEqual(self.line(NO_COLOR="1", MERWITCH_MOTIF="cyberpunk"),
                         ":(=^.^=): rocheverse:~$ Opus · ctx ████░░░░░░ 42% · $0.42 · LORE")
        self.assertEqual(self.line(NO_COLOR="1", MERWITCH_MOTIF="y2k-blog"),
                         "[merwitch.exe] :(=^.^=): mood ✧ | Opus | ctx ♥♥♥♥♡♡♡♡♡♡ 42% | $0.42 | visitor no. 000,000")

    def test_colour_is_plum_ground_with_signatures(self):
        plum = "48;2;80;22;60"
        for motif, sig in (("analog", "GUEST CHECK"), ("cyberpunk", "rocheverse:~$"), ("y2k-blog", "merwitch.exe")):
            out = self.line(MERWITCH_MOTIF=motif)
            self.assertIn(plum, out, motif)
            self.assertIn(sig, out, motif)
            self.assertNotIn("\033[5m", out)              # no blink
            self.assertNotIn("255;45;138", out)           # retired hot pink
        cyber = self.line(MERWITCH_MOTIF="cyberpunk")
        self.assertIn("38;2;254;157;202m█", cyber)        # candy block cursor
        self.assertIn("░▒", cyber)

    def test_motif_order_env_config_style_alias(self):
        self.write("config.json", {"motif": "y2k-blog"})
        self.assertIn("merwitch.exe", self.line(NO_COLOR="1"))
        self.assertIn(":~$", self.line(NO_COLOR="1", MERWITCH_MOTIF="cyberpunk"))
        self.write("config.json", {})
        old = self.write("old.json", {"motif": "retro-tv"})
        self.assertIn(":~$", self.line(NO_COLOR="1", ROCHA_CODED_STYLE=old))
        self.assertIn("GUEST CHECK", self.line(NO_COLOR="1", MERWITCH_MOTIF="glitter"))

    def test_defensive_input(self):
        for bad in ("", "garbage", "[]", '{"model": 7, "cost": "x", "context_window": null}'):
            out = self.line(stdin=bad, NO_COLOR="1", MERWITCH_MOTIF="cyberpunk")
            self.assertTrue(out.startswith(":(=^.^=):"), repr(bad))
        out = self.line(stdin='{"context_window":{"total_input_tokens":50000,"context_window_size":200000}}', NO_COLOR="1",
                        MERWITCH_MOTIF="cyberpunk")
        self.assertIn("ctx ███░░░░░░░ 25%", out)
        self.assertNotIn("$", out.replace(":~$", ""))   # no cost, no empty slot

    def test_low_context_turns_gold(self):
        out = self.line(stdin='{"context_window":{"used_percentage":91}}', MERWITCH_MOTIF="cyberpunk")
        self.assertIn("38;2;233;185;73;48;2;80;22;60mctx", out)

    def test_visitor_counter_reads_state(self):
        self.write("state.json", {"visitors": 777})
        self.assertIn("visitor no. 000,777", self.line(NO_COLOR="1", MERWITCH_MOTIF="y2k-blog"))

    def test_sparkle_glyph(self):
        self.write("config.json", {"glyph": "sparkle"})
        self.assertIn("∴(=^･✧･^=)∴", self.line(NO_COLOR="1"))

    def test_pairs_with_pocket_familiar(self):
        fake = self.tmp / "familiar"
        fake.write_text('import os\nprint(" ∴(=^･✧･^=)∴ Lucky  fed  · streak 3d · Opus " if os.environ.get("NO_COLOR") else "colour")\n')
        out = self.line(NO_COLOR="1", MERWITCH_PAIR="1", MERWITCH_FAMILIAR=str(fake), MERWITCH_MOTIF="cyberpunk")
        self.assertTrue(out.startswith("∴(=^･✧･^=)∴ Lucky fed rocheverse:~$"), out)
        egg = self.tmp / "egg"
        egg.write_text('print(" (  ✧  ) an egg · run familiar hatch")\n')
        out = self.line(NO_COLOR="1", MERWITCH_PAIR="1", MERWITCH_FAMILIAR=str(egg))
        self.assertTrue(out.startswith(":(=^.^=):"), out)
        out = self.line(NO_COLOR="1", MERWITCH_PAIR="0", MERWITCH_FAMILIAR=str(fake))
        self.assertTrue(out.startswith(":(=^.^=):"), out)

    def test_user_style_never_borrows_her_words(self):
        user = self.write("style.json", {"name": "", "palette": {"hero": "#123456"}, "lines": {}})
        for motif in ms.MOTIFS:
            out = self.line(ROCHA_CODED_STYLE=user, MERWITCH_MOTIF=motif)
            for word in HER_WORDS:
                self.assertNotIn(word, out, motif)
            self.assertIn("48;2;18;52;86", out)            # her own ground colour
        self.assertIn("my-world:~$", self.line(ROCHA_CODED_STYLE=user, MERWITCH_MOTIF="cyberpunk"))

    def test_style_json_in_session_folder(self):
        (self.tmp / "proj").mkdir()
        (self.tmp / "proj" / "style.json").write_text(json.dumps(
            {"name": "Ocean Desk", "palette": {"hero": "#0077B6"}, "lines": {"stamp": "TIDE"}}))
        stdin = json.dumps({"model": {"display_name": "Opus"}, "workspace": {"current_dir": str(self.tmp / "proj")}})
        env = {k: v for k, v in self.env.items() if k != "ROCHA_CODED_STYLE"}
        out = subprocess.run(["bash", str(ROOT / "statusline.sh")], input=stdin, capture_output=True, text=True,
                             env={**env, "HOME": str(self.tmp), "MERWITCH_MOTIF": "cyberpunk"}).stdout
        self.assertIn("0;119;182", out)
        self.assertIn("TIDE", out)
        self.assertIn("ocean-desk:~$", out)


class StyleLoader(Base):
    def test_inheritance_rule(self):
        path = self.write("partial.json", {"name": "", "owner": "", "palette": {"hero": "#123456", "ink": "nope"},
                                           "fonts": {"masthead": "Bodoni Moda"}, "lines": {}})
        style, _ = ms.load_style(path)
        her, _ = ms.load_style(BUNDLED)
        self.assertEqual(style["palette"]["hero"], "#123456")
        self.assertEqual(style["palette"]["ink"], her["palette"]["ink"])        # bad hex falls back
        self.assertEqual(style["palette"]["gold"], her["palette"]["gold"])      # missing colour falls back
        self.assertEqual(style["fonts"]["masthead"], "Bodoni Moda")
        self.assertEqual(style["fonts"]["mono"], her["fonts"]["mono"])
        self.assertEqual(style["lines"], {})
        for key in ("owner", "handle", "name", "references", "notes"):
            self.assertFalse(style.get(key), key)
        self.assertEqual(ms.world(style), "my-world")

    def test_example_files_share_keys(self):
        a = json.loads(Path(BUNDLED).read_text())
        b = json.loads((ROOT / "style.example.json").read_text())
        self.assertEqual(set(a), set(b))
        for key in ("palette", "fonts", "lines"):
            self.assertEqual(set(a[key]), set(b[key]), key)

    def test_bundled_example_identical_to_reference(self):
        ref = ROOT.parent / "ai-recommends-you" / "examples" / "style.rocha-coded.json"
        if ref.exists():
            self.assertEqual(Path(BUNDLED).read_bytes(), ref.read_bytes())


class Omen(Base):
    def test_same_all_day_and_her_lines_only(self):
        style, _ = ms.load_style(BUNDLED)
        words = ms.load_words(str(ROOT / "words.json"))
        day = date(2026, 10, 31)
        a, b = om.omen(style, words, day, "analog"), om.omen(style, words, day, "analog")
        self.assertEqual(a, b)
        body = a.split("✂┈ ", 1)[1]
        line = body.split(": ", 1)[1]
        self.assertIn(line, om.omen_lines(style))
        self.assertIn(body.split(": ", 1)[0], words["omen_openers"])
        seen = {om.omen(style, words, date(2026, 11, d), "analog") for d in range(1, 29)}
        self.assertGreater(len(seen), 3)

    def test_three_motifs(self):
        for motif, sig in (("analog", "GUEST CHECK"), ("cyberpunk", "rocheverse:~$ omen --today"),
                           ("y2k-blog", "[merwitch.exe] mood: ✧")):
            out = self.run_py("omen.py", "--motif", motif, "--date", "2026-10-31").stdout
            self.assertIn(sig, out)
            self.assertIn("last quarter", out)

    def test_user_style_without_lines_is_quiet_not_hers(self):
        user = self.write("u.json", {"lines": {}})
        out = self.run_py("omen.py", "--style", user, "--motif", "cyberpunk").stdout
        for word in HER_WORDS:
            self.assertNotIn(word, out)
        self.assertIn("the cards are quiet today", out)
        mine = self.write("m.json", {"name": "Ocean Desk", "lines": {"affirm": "salt water heals"}})
        self.assertIn("salt water heals", self.run_py("omen.py", "--style", mine).stdout)

    def test_moon_phases(self):
        self.assertEqual(om.moon_phase(date(2000, 1, 6)), "new moon")
        self.assertEqual(om.moon_phase(date(2026, 10, 26)), "full moon")
        self.assertEqual(self.run_py("omen.py", "--date", "31-10-2026").returncode, 2)


class Hooks(Base):
    def test_greet_counts_visits_and_shows_message(self):
        r = self.run_py("hooks.py", "greet", stdin='{"source":"startup"}')
        msg = json.loads(r.stdout)["systemMessage"]
        self.assertTrue(msg.startswith(":(=^.^=): "))
        self.run_py("hooks.py", "greet", stdin='{"source":"resume"}')
        self.run_py("hooks.py", "greet", stdin="not json")
        self.assertEqual(json.loads((self.tmp / "state.json").read_text())["visitors"], 2)

    def test_chime_off_by_default_and_on_when_asked(self):
        marker = self.tmp / "played.txt"
        fake = self.tmp / "player.sh"
        fake.write_text(f'#!/bin/bash\necho "$1" >> "{marker}"\n')
        fake.chmod(0o755)
        for kind in ("done", "notify"):
            r = self.run_py("hooks.py", kind, MERWITCH_PLAYER=str(fake))
            self.assertEqual((r.returncode, r.stdout), (0, ""))
        self.assertFalse(marker.exists())
        self.write("config.json", {"chime": True})
        self.run_py("hooks.py", "done", MERWITCH_PLAYER=str(fake))
        self.run_py("hooks.py", "notify", MERWITCH_PLAYER=str(fake))
        for _ in range(50):
            if marker.exists() and len(marker.read_text().split()) == 2:
                break
            subprocess.run(["sleep", "0.1"])
        played = marker.read_text().split()
        self.assertTrue(any(p.endswith("chime.wav") for p in played) and any(p.endswith("bell.wav") for p in played))

    def test_hook_never_fails(self):
        r = self.run_py("hooks.py", "greet", stdin="{", MERWITCH_WORDS=str(self.tmp / "missing.json"))
        self.assertEqual(r.returncode, 0)
        self.assertEqual(self.run_py("hooks.py", "nonsense").returncode, 0)


class Sounds(Base):
    def test_generated_wavs(self):
        out = self.tmp / "gen"
        shutil.copytree(ROOT / "scripts", out / "scripts")
        subprocess.run([sys.executable, str(out / "scripts" / "make-chime.py")], check=True, capture_output=True)
        for name, low, high in (("chime.wav", 1.0, 1.6), ("bell.wav", 0.6, 1.2)):
            with wave.open(str(out / "sounds" / name)) as w:
                self.assertEqual((w.getnchannels(), w.getsampwidth(), w.getframerate()), (1, 2, 22050))
                self.assertTrue(low <= w.getnframes() / 22050 <= high)
            self.assertEqual((out / "sounds" / name).read_bytes(), (ROOT / "sounds" / name).read_bytes(), name)


class Install(Base):
    def install(self, *args, home=None):
        home = home or self.tmp / "home"
        return subprocess.run(["bash", str(ROOT / "install.sh"), *args], capture_output=True, text=True,
                              env={**os.environ, "HOME": str(home)}, timeout=60)

    def settings(self):
        return json.loads((self.tmp / "home" / ".claude" / "settings.json").read_text())

    def backups(self):
        return sorted((self.tmp / "home" / ".claude").glob("settings.json.backup-*"))

    def test_install_idempotent_uninstall_restores(self):
        claude = self.tmp / "home" / ".claude"
        claude.mkdir(parents=True)
        (claude / "settings.json").write_text(json.dumps({
            "model": "opus", "statusLine": {"type": "command", "command": "echo old"},
            "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo keep-me"}]}]}}))
        r = self.install("--motif", "cyberpunk")
        self.assertEqual(r.returncode, 0, r.stderr)
        s = self.settings()
        self.assertIn("merwitch-mode/statusline.sh", s["statusLine"]["command"])
        for event, kind in (("SessionStart", "greet"), ("Stop", "done"), ("Notification", "notify")):
            cmds = [h["command"] for g in s["hooks"][event] for h in g["hooks"]]
            self.assertTrue(any(c.endswith(f"hooks.py {kind}") for c in cmds), event)
        self.assertIn("echo keep-me", json.dumps(s["hooks"]["Stop"]))
        self.assertEqual(s["spinnerVerbs"]["mode"], "replace")
        self.assertIn("Stirring the cauldron", s["spinnerVerbs"]["verbs"])
        self.assertEqual(s["model"], "opus")
        self.assertEqual(len(self.backups()), 1)
        cmd = (claude / "commands" / "merwitch.md").read_text()
        self.assertIn("omen.py", cmd)
        self.assertIn("allowed-tools", cmd)
        cfg = json.loads((claude / "merwitch-mode" / "config.json").read_text())
        self.assertEqual((cfg["motif"], cfg["chime"]), ("cyberpunk", False))
        # the installed copy runs on its own
        out = subprocess.run(["bash", str(claude / "merwitch-mode" / "statusline.sh")], input=SAMPLE, text=True,
                             capture_output=True, env={**os.environ, "HOME": str(self.tmp / "home"), "NO_COLOR": "1",
                                                       "MERWITCH_PAIR": "0"}).stdout
        self.assertIn(":~$ Opus", out)
        omen = subprocess.run([sys.executable, str(claude / "merwitch-mode" / "omen.py")], capture_output=True,
                              text=True, env={**os.environ, "HOME": str(self.tmp / "home")})
        self.assertIn(":~$ omen --today", omen.stdout)
        # twice changes nothing
        before = (claude / "settings.json").read_text()
        r = self.install()
        self.assertIn("already installed", r.stdout)
        self.assertEqual((claude / "settings.json").read_text(), before)
        self.assertEqual(len(self.backups()), 1)
        # her edited words survive a reinstall and become the thinking words
        words = json.loads((claude / "merwitch-mode" / "words.json").read_text())
        words["thinking"] = ["Pulling a tarot card"]
        (claude / "merwitch-mode" / "words.json").write_text(json.dumps(words))
        self.install("--chime", "on")
        self.assertEqual(self.settings()["spinnerVerbs"]["verbs"], ["Pulling a tarot card"])
        self.assertTrue(json.loads((claude / "merwitch-mode" / "config.json").read_text())["chime"])
        # uninstall puts everything back the way it was
        r = self.install("--uninstall")
        self.assertEqual(r.returncode, 0, r.stderr)
        s = self.settings()
        self.assertEqual(s, {"model": "opus", "statusLine": {"type": "command", "command": "echo old"},
                             "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo keep-me"}]}]}})
        self.assertFalse((claude / "commands" / "merwitch.md").exists())
        self.assertEqual([p.name for p in (claude / "merwitch-mode").iterdir()], ["words.json"])
        self.assertIn("nothing of merwitch-mode", self.install("--uninstall").stdout)

    def test_fresh_home_and_bad_settings(self):
        r = self.install()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(self.backups(), [])          # nothing existed, so nothing to back up
        self.install("--uninstall")
        self.assertNotIn("statusLine", self.settings())
        self.assertNotIn("spinnerVerbs", self.settings())
        bad = "{ this is not json"
        (self.tmp / "home" / ".claude" / "settings.json").write_text(bad)
        r = self.install()
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual((self.tmp / "home" / ".claude" / "settings.json").read_text(), bad)

    def test_her_own_spinner_words_come_back(self):
        claude = self.tmp / "home" / ".claude"
        claude.mkdir(parents=True)
        theirs = {"mode": "append", "verbs": ["Vibing"]}
        (claude / "settings.json").write_text(json.dumps({"spinnerVerbs": theirs}))
        self.install()
        self.install("--glyph", "sparkle")
        self.assertEqual(self.settings()["spinnerVerbs"]["mode"], "replace")
        self.install("--uninstall")
        self.assertEqual(self.settings()["spinnerVerbs"], theirs)

    def test_bad_options_are_refused_kindly(self):
        for args in (("--motif", "glitter"), ("--chime", "loud"), ("--nope",)):
            r = self.install(*args)
            self.assertNotEqual(r.returncode, 0)
            self.assertFalse((self.tmp / "home" / ".claude" / "settings.json").exists())


class Themes(Base):
    def test_themes_from_a_second_palette(self):
        style = self.write("ocean.json", {"name": "Ocean Desk", "palette": {"hero": "#0077B6", "paper": "#FFFFFF"}})
        r = self.run_py("themes/make-themes.py", "--style", style, "--out", str(self.tmp / "t"))
        self.assertEqual(r.returncode, 0, r.stderr)
        plist = self.tmp / "t" / "ocean-desk.itermcolors"
        d = plistlib.loads(plist.read_bytes())
        self.assertEqual(len([k for k in d if k.startswith("Ansi ")]), 16)
        self.assertAlmostEqual(d["Background Color"]["Blue Component"], 0xB6 / 255)
        if shutil.which("plutil"):
            self.assertEqual(subprocess.run(["plutil", "-lint", str(plist)], capture_output=True).returncode, 0)
        self.assertIn("background = #0077B6", (self.tmp / "t" / "ocean-desk.ghostty").read_text())
        self.assertIn("background: '#0077B6'", (self.tmp / "t" / "ocean-desk.yaml").read_text())

    def test_shipped_themes_match_the_generator(self):
        self.run_py("themes/make-themes.py", "--style", BUNDLED, "--out", str(self.tmp / "rc"))
        for ext in ("itermcolors", "ghostty", "yaml"):
            self.assertEqual((self.tmp / "rc" / f"rocha-coded.{ext}").read_bytes(),
                             (ROOT / "themes" / f"rocha-coded.{ext}").read_bytes(), ext)
        if shutil.which("plutil"):
            r = subprocess.run(["plutil", "-lint", str(ROOT / "themes" / "rocha-coded.itermcolors")], capture_output=True)
            self.assertEqual(r.returncode, 0)


class Wallpaper(Base):
    def test_three_motifs_valid_with_signatures(self):
        for motif, sig in (("analog", "VOL. 1 · NO. 001"), ("cyberpunk", "rocheverse:~$"),
                           ("y2k-blog", "you are visitor no. 000,777")):
            out = self.tmp / f"{motif}.svg"
            self.run_py("make-wallpaper.py", "--style", BUNDLED, "--motif", motif, "--out", str(out))
            xml.dom.minidom.parse(str(out))
            text = out.read_text()
            self.assertIn(sig, text)
            self.assertNotRegex(text.lower(), "feGaussianBlur|glow")

    def test_user_wallpaper_has_none_of_her_words(self):
        user = self.write("u.json", {"palette": {"hero": "#123456"}, "lines": {}})
        for motif in ms.MOTIFS:
            out = self.tmp / f"u-{motif}.svg"
            self.run_py("make-wallpaper.py", "--style", user, "--motif", motif, "--out", str(out))
            text = out.read_text()
            for word in HER_WORDS:
                self.assertNotIn(word, text, motif)
            self.assertIn(ms.PLACEHOLDER, text)


class House(Base):
    def test_no_em_dashes_or_banned_words(self):
        for path in ROOT.rglob("*"):
            if path.is_file() and path.suffix in (".md", ".py", ".sh", ".json") and ".git" not in path.parts:
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(chr(0x2014), text, path)
                for word in (" simply ", " just ", "undocumented", "helpers"):
                    if path.name != "test_merwitch.py":
                        self.assertNotIn(word, text.lower(), f"{word} in {path}")


if __name__ == "__main__":
    unittest.main()
