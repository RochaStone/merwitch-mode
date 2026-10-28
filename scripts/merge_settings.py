#!/usr/bin/env python3
"""Safely adds or removes merwitch-mode in a Claude Code settings.json.

Based on the settings merge script in the pink-terminal sibling kit (MIT). The rules:
  1. A timestamped backup is written before anything changes, and only when something changes.
  2. If the file is not valid JSON, nothing is written and the script exits 2.
  3. Running the same install twice changes nothing (idempotent).
  4. The new file goes to a temp file first and is moved into place, so a crash never leaves half a file.
  5. Your other hooks are kept. A status line you had before is saved and comes back on uninstall.

  merge_settings.py install   --settings F --home RUNTIME_DIR --words WORDS_JSON
  merge_settings.py uninstall --settings F --home RUNTIME_DIR
"""
import argparse
import json
import os
import shlex
import shutil
import sys
import tempfile
import time

MARK = "merwitch-mode/"
HOOKS = (("SessionStart", "greet"), ("Stop", "done"), ("Notification", "notify"))


def load(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as err:
        print(f"your settings file is not valid JSON, so nothing was changed: {path} ({err})", file=sys.stderr)
        sys.exit(2)
    if not isinstance(data, dict):
        print(f"your settings file is not a JSON object, so nothing was changed: {path}", file=sys.stderr)
        sys.exit(2)
    return data


def save(path, data):
    folder = os.path.dirname(os.path.abspath(path))
    os.makedirs(folder, exist_ok=True)
    if os.path.exists(path):
        backup = f"{path}.backup-{time.strftime('%Y%m%d-%H%M%S')}"
        n = 1
        while os.path.exists(backup):
            backup = f"{path}.backup-{time.strftime('%Y%m%d-%H%M%S')}-{n}"
            n += 1
        shutil.copy2(path, backup)
        print(f"backup saved: {backup}")
    fd, tmp = tempfile.mkstemp(dir=folder, prefix=".settings-", suffix=".json")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    os.replace(tmp, path)


def read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else None
    except (OSError, ValueError):
        return None


def ours(cmd):
    return isinstance(cmd, str) and MARK in cmd


def thinking_words(words_path):
    try:
        with open(words_path, encoding="utf-8") as fh:
            words = json.load(fh).get("thinking", [])
    except (OSError, ValueError, AttributeError):
        words = []
    return [str(w).strip()[:40] for w in words if str(w).strip()][:40]


def install(args):
    data = load(args.settings)
    before = json.dumps(data, sort_keys=True)
    home = os.path.abspath(args.home)
    status_cmd = f"bash {shlex.quote(os.path.join(home, 'statusline.sh'))}"
    current = data.get("statusLine")
    if current and not ours((current or {}).get("command") if isinstance(current, dict) else None):
        with open(os.path.join(home, "previous-statusline.json"), "w", encoding="utf-8") as fh:
            json.dump(current, fh, indent=2)
        print("your previous status line is saved and comes back if you uninstall")
    data["statusLine"] = {"type": "command", "command": status_cmd, "padding": 0}
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        hooks = {}
    for event, kind in HOOKS:
        cmd = f"python3 {shlex.quote(os.path.join(home, 'hooks.py'))} {kind}"
        groups = [g for g in hooks.get(event, []) if isinstance(g, dict)]
        for g in groups:   # drop an older merwitch hook (for example from another folder), keep everyone else's
            g["hooks"] = [h for h in g.get("hooks", []) if not ours(h.get("command"))]
        groups = [g for g in groups if g.get("hooks")]
        groups.append({"hooks": [{"type": "command", "command": cmd, "timeout": 10}]})
        hooks[event] = groups
    data["hooks"] = hooks
    verbs = thinking_words(args.words)
    if verbs:
        prev = data.get("spinnerVerbs")
        record = os.path.join(home, "spinner-written.json")
        written = read(record)
        if prev and prev != written and prev != {"mode": "replace", "verbs": verbs}:
            with open(os.path.join(home, "previous-spinner.json"), "w", encoding="utf-8") as fh:
                json.dump(prev, fh, indent=2)   # someone else's words: keep them for uninstall
        data["spinnerVerbs"] = {"mode": "replace", "verbs": verbs}
        with open(record, "w", encoding="utf-8") as fh:
            json.dump(data["spinnerVerbs"], fh, indent=2)
    if json.dumps(data, sort_keys=True) == before:
        print("already installed, nothing to change")
        return
    save(args.settings, data)
    print(f"status line, 3 hooks and {len(verbs)} thinking words added to {args.settings}")


def uninstall(args):
    data = load(args.settings)
    before = json.dumps(data, sort_keys=True)
    home = os.path.abspath(args.home)
    current = data.get("statusLine")
    if isinstance(current, dict) and ours(current.get("command")):
        prev = os.path.join(home, "previous-statusline.json")
        try:
            with open(prev, encoding="utf-8") as fh:
                data["statusLine"] = json.load(fh)
            print("your previous status line is back")
        except (OSError, ValueError):
            data.pop("statusLine", None)
    hooks = data.get("hooks")
    if isinstance(hooks, dict):
        for event in list(hooks):
            groups = []
            for g in hooks[event] if isinstance(hooks[event], list) else []:
                if isinstance(g, dict):
                    g["hooks"] = [h for h in g.get("hooks", []) if not ours(h.get("command"))]
                    if g["hooks"]:
                        groups.append(g)
            if groups:
                hooks[event] = groups
            else:
                del hooks[event]
        if not hooks:
            data.pop("hooks", None)
    spin = data.get("spinnerVerbs")
    if isinstance(spin, dict) and spin == read(os.path.join(home, "spinner-written.json")):   # only our own words
        prev = read(os.path.join(home, "previous-spinner.json"))
        if prev:
            data["spinnerVerbs"] = prev
        else:
            data.pop("spinnerVerbs", None)
    if json.dumps(data, sort_keys=True) == before:
        print("nothing of merwitch-mode in your settings")
        return
    save(args.settings, data)
    print(f"merwitch-mode removed from {args.settings}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="action", required=True)
    i = sub.add_parser("install")
    i.add_argument("--settings", required=True)
    i.add_argument("--home", required=True)
    i.add_argument("--words", required=True)
    u = sub.add_parser("uninstall")
    u.add_argument("--settings", required=True)
    u.add_argument("--home", required=True)
    args = p.parse_args()
    install(args) if args.action == "install" else uninstall(args)


if __name__ == "__main__":
    main()
