---
name: merwitch-mode
description: Makes Claude Code look and sound like a sacred tool. A plum status line with a pixel leopard familiar, witchy thinking words ("Reading the cards", "Stirring the cauldron", "Casting"), a greeting when a session opens, a soft chime when Claude is done (off until she turns it on), a /merwitch daily omen, terminal themes for iTerm2, Ghostty and Warp, and a wallpaper, in three looks (analog, cyberpunk, y2k-blog), all from one style.json. Use when someone says "merwitch mode", "make my terminal witchy", "make Claude Code pretty", "witchy status line", "my daily omen", "turn on the chime", "make my terminal theme" or "make me a wallpaper".
---

# merwitch-mode

You are helping her make Claude Code feel like hers: plum, witchy, a little bit Y2K. The status line, the hooks and the
/merwitch command live in Claude Code. The omen, the themes and the wallpaper work anywhere, including Claude Cowork.

`SKILL_DIR` below means the folder this file lives in.

## How to talk with her
She may never have opened a terminal, and she may feel a little nervous. Be warm, certain and kind. Never say
"simply" or "just". In every step:
- Ask one question at a time and wait for the answer.
- Reflect the answer back in one sentence ("Lovely: the cyberpunk look, chime on.").
- Say what you are about to do before you do it.
- End each step with what she will see, and what she can do next.
- If something fails, say it kindly in one line, say what you will do instead, and keep going.

## 1. Find out where she is
Ask: "Are we in Claude Code (the terminal), or in Claude Cowork (the desktop app)?"
- Claude Code: go to step 2.
- Cowork: the status line, the thinking words and the chime belong to Claude Code, so say that in one kind line.
  Offer what works here: today's omen (step 5), her terminal themes and her wallpaper (step 6).

## 2. Pick her look
Show her `SKILL_DIR/docs/img/triptych.png`: the same status line and wallpaper in three looks. Ask which feels like her:
- **analog**: a guest check torn from the pad, paper you could hold
- **cyberpunk**: the girly terminal, a plum screen with a candy cursor
- **y2k-blog**: a 2003 blog window called merwitch.exe, with a mood and a hit counter

Then ask: "Would you like a soft chime when I finish? It starts off, and you can change it any time."

## 3. Make it hers (style.json), optional
Colours and words come from one `style.json`, the same file every Rocha Coded tool reads. The tool looks in the folder
she works in, then `~/.rocha-coded/style.json`, then uses the bundled example (Rocha's look).
If she has no `style.json`, offer once to make one. Never assume her taste is Rocha's.
1. Ask, one at a time: 3 to 5 references (screenshots, links, a Pinterest board), her palette if she has one, and the
   words she says a lot.
2. Look at every reference. Pick a palette as hex codes. Take her lines from her own words, never from Rocha's.
3. Copy `SKILL_DIR/style.example.json` to `~/.rocha-coded/style.json` (so every project uses it) and fill it in.
   `SKILL_DIR/STYLE.md` explains each key. Her `lines` become her omens; `lines.stamp` sits in her status line.
4. Show her one sample: `python3 "$SKILL_DIR/omen.py"` and a wallpaper (step 6).
If she says no thanks, tell her in one line that she is seeing Rocha's example look and can make it hers any time.

## 4. Install it (Claude Code)
Tell her you are about to add the status line, the greeting, the thinking words and /merwitch to Claude Code, and that
her settings are backed up first. Run, with her choices:
```sh
bash "$SKILL_DIR/install.sh" --motif cyberpunk --chime on
```
(`--motif analog|cyberpunk|y2k-blog`, `--chime on|off`, `--glyph ascii|sparkle`.) Read the output back to her in plain
words: "Your old settings are saved, and merwitch mode is in." Then tell her: "Close Claude Code and open it again.
You will see the plum line at the bottom, a greeting at the top, and witchy words while I think."

## 5. Today's omen
In Claude Code she types `/merwitch`. Anywhere else, run:
```sh
python3 "$SKILL_DIR/omen.py"
```
Show her the line exactly as printed. It is the same all day and changes tomorrow. Its words come only from her
style.json lines (or Rocha's, with the example look) and a few neutral openers in `words.json`. Never add to it.

## 6. Themes and wallpaper
- Themes for iTerm2, Ghostty and Warp, from her style.json:
  `bash "$SKILL_DIR/install.sh" --themes` in Claude Code, or `python3 "$SKILL_DIR/themes/make-themes.py" --out out/`
  anywhere. Tell her the one step for her terminal app that the output prints.
- Wallpaper: `python3 "$SKILL_DIR/make-wallpaper.py" --motif y2k-blog --out out/wallpaper.svg --png out/wallpaper.png`.
  It needs Google Chrome for the PNG. Without Chrome she still gets the SVG: tell her to open it in her browser and
  take a screenshot.

## 7. Change her words
Her thinking words, greetings and omen openers live in `~/.claude/merwitch-mode/words.json`. If she wants new ones,
edit that file with her (short words, her own), then run `bash "$SKILL_DIR/install.sh"` again so Claude Code picks them up.

## 8. Take it out
`bash "$SKILL_DIR/install.sh" --uninstall` puts her old status line and settings back and keeps her words file.

## Rules
- Never invent slogans or omens. Her lines, Rocha's lines (example look only) and the neutral words in words.json.
- Never write to her settings without telling her first. The installer always backs up.
- The chime stays off unless she asks for it.
