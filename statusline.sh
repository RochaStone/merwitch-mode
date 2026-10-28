#!/bin/bash
# merwitch-mode status line. Claude Code runs this and pipes its session JSON in.
# If anything goes wrong it still prints the leopard, so the status bar never goes blank.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
out="$(python3 "$DIR/statusline.py" 2>/dev/null)"
printf '%s\n' "${out:-:(=^.^=):}"
exit 0
