# Testing

Everything below was run on 28 Oct 2026, on macOS with Python 3.12.8, Google Chrome installed and Claude Code 2.1.311.

## 1. The tests
```sh
python3 -m unittest discover -s tests -v
```
Result: **30 tests, all OK.** They cover:
- **Status line, all three motifs** from one function, with sample Claude Code JSON: the exact plain-text line for analog (GUEST CHECK), cyberpunk (`rocheverse:~$`) and y2k-blog (`merwitch.exe`, visitor counter); in colour, the plum ground in every motif, the candy block cursor and dither edge in cyberpunk, no blink code, no retired hot pink
- **Defensive input:** empty, garbage, a JSON list and wrong types all still print the leopard; context worked out from token counts when no percentage comes in; missing cost leaves no empty slot; gold type at 80% context or more
- **Motif order:** `MERWITCH_MOTIF`, then config.json, then style.json; old names map to their family; an unknown name falls back to analog
- **Pairing:** a fake pocket-familiar's sprite and mood replace the leopard; an unhatched egg or pairing switched off keeps the leopard
- **Inheritance rule:** a user style borrows only missing or malformed colours and fonts; her lines, owner, handle, name, references and notes never borrow; a user style with no lines shows none of Rocha's words in any motif of the status line, the omen or the wallpaper; a style.json in the session folder is picked up
- **Omen:** the same all day, drawn only from the style's lines and the openers in words.json, varied across a month, three motif markers, a quiet line (never hers) for a style with no lines, moon phase checked on a known new moon (6 Jan 2000) and full moon (26 Oct 2026), and a kind refusal of a bad date
- **Hooks:** the greeting prints valid JSON with a `systemMessage`, counts new sessions but not resumes, survives bad input; the chime and bell do not play by default and do play (through a fake player) when the chime is on; hooks always exit 0
- **Sounds:** the generator rebuilds both WAVs byte for byte: mono, 16-bit, 22050 Hz, the right length
- **Install against a fake HOME:** status line, three hooks, twelve thinking words (`spinnerVerbs`) and the /merwitch command file added; her other hooks and settings kept; one backup; the installed copy runs on its own; a second install changes nothing and makes no new backup; edited words survive a reinstall and become the thinking words; `--chime on` is saved; uninstall restores her previous status line and settings exactly and keeps only words.json; spinner words she had before come back on uninstall; invalid settings JSON is never overwritten; bad options are refused before anything is written
- **Themes:** all three files from a second palette, the iTerm2 plist read by Python and passed by `plutil -lint`; the shipped themes are exactly the generator's output
- **Wallpaper:** all three motifs are valid SVG with their signatures and no glow filters
- **House rules:** no em dashes, "simply", "just", "undocumented" or "helpers" in any text file

## 2. By eye
- `python3 scripts/make-readme-images.py` rendered the hero (1200x620) and the triptych (1620x480) with headless Chrome. Both were opened and checked: the status lines in the pictures are the real output of `statusline.py`, nothing cut off, no glow.
- The y2k-blog wallpaper was rendered to PNG at 1280x800 through `make-wallpaper.py --png` and checked.
- `sounds/chime.wav` was played with `afplay`: a soft two-note bell, no click at the end.
- The status line was run in all three motifs in a real terminal (truecolour): plum ground, cream and ink type, gold prompt.

## 3. Security gate
```sh
./scripts/security-check.sh
```
Result: 9 passed, 0 failed, **SAFE TO PUBLISH**.

## Not tested
- **A live Claude Code session** with merwitch mode installed. The installer was run only against fake home folders, never against the real `~/.claude`. The `spinnerVerbs` setting, the hook `systemMessage` field and the `!` command syntax were checked against the Claude Code 2.1.311 build on this machine, not seen on screen.
- **Linux sound** (`paplay`, `aplay`): the code path is the same as macOS with a different player, tested only with a fake player.
- **Ghostty and Warp** loading the theme files: the files match the formats those apps document; only the iTerm2 file was linted.
- **Claude Cowork** upload of the zip.
- **The real pocket-familiar** pairing: tested with a fake `familiar` that prints the same line shape.
- Windows.
