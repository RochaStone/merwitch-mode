# style.json

One file holds your look. Every Rocha Coded tool reads the same file, so you make it once.

## Where it goes
The tool looks in this order and uses the first one it finds:
1. `style.json` in the folder you are working in (the status line checks the folder your Claude Code session is in)
2. `~/.rocha-coded/style.json`, to use one look across every project (recommended for merwitch-mode)
3. `examples/style.rocha-coded.json`, the bundled example (Rocha's look)

Start from `style.example.json`: copy it to `~/.rocha-coded/style.json` and fill it in. Or ask Claude to make one with you.

## The keys
| Key | What to put there | Used by merwitch-mode |
|---|---|---|
| `name` | your brand or studio name | the theme file names, and your prompt name if `lines.magazine` is empty |
| `owner` | your name, as you sign things | "about me" on the y2k-blog wallpaper |
| `handle`, `site` | your handle and website | no |
| `palette.hero` | your ground colour, the deep one everything sits on | the status line ground, the terminal background, the wallpaper |
| `palette.paper` | a light paper colour | type on the ground, the y2k-blog window |
| `palette.paper_pink` | a second paper colour | the analog guest check strip, the y2k tile |
| `palette.ink` | your text colour | type on paper |
| `palette.accent` | your one bright accent | the leopard, the block cursor, the terminal cursor |
| `palette.wine` | a second deep colour | the dither edge, the stamp, the selection colour |
| `palette.gold` | a highlight colour | the prompt, the window buttons, low-context warning |
| `palette.marker` | a scrawl colour | the y2k leopard, the analog low-context warning |
| `palette.plum`, `palette.cool` | a deep shade, a cool accent | the terminal theme's blue and spare slots |
| `fonts.*` | Google Fonts names | the wallpaper (the terminal uses your terminal's own font) |
| `motif` | `analog`, `cyberpunk` or `y2k-blog` (older names still work and map to the nearest one) | the look, unless you pick one with `install.sh --motif` |
| `lines.stamp` | one short word | the stamp at the end of your status line |
| `lines.magazine` | your world's name | your prompt, like `yourworld:~$` |
| `lines.headline`, `scrawl`, `todo`, `celebrate`, `affirm` | your own lines | your daily omens, and the wallpaper |
| `lines.masthead` | a newspaper masthead | the analog wallpaper |
| `lines.invite` | invitation text | no |
| `references`, `notes` | images or links that feel like you, and your look in a sentence | Claude reads these when it makes your style with you |

## Good to know
- Colours must be hex codes (`#RRGGBB`). Anything else is skipped and the bundled colour is used for that slot.
- Any colour or font you leave empty borrows the bundled example's, so everything always looks finished.
- Your words and your name never borrow. Leave `lines` empty and your omen says the cards are quiet, and the
  wallpaper says YOUR WORDS HERE. Rocha's words appear only when you use her bundled example whole.
- `words.json` (installed at `~/.claude/merwitch-mode/words.json`) holds the thinking words, greetings and omen openers.
  Edit it, then run `./install.sh` again.
