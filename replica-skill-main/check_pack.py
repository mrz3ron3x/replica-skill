#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Ahmii Labs. See LICENSE.
"""Integrity check for the whole Replica pack. Standard library only.

Checks the license and its copyright notices, the SPDX header on every Python
and TypeScript file, each skill's frontmatter, the plugin manifests, every
relative markdown link, and that no em dash slipped in. Exits 1 on any problem
so it can run in CI or before a release.

    python3 check_pack.py
    python3 check_pack.py /path/to/replica-skill --json
"""

import argparse
import json
import os
import re
import sys

EM_DASH = chr(0x2014)
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv"}


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for fn in sorted(filenames):
            yield os.path.join(dirpath, fn)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def check_license(root):
    path = os.path.join(root, "LICENSE")
    if not os.path.isfile(path):
        return ["LICENSE is missing"]
    text = read(path)
    problems = []
    if "MIT License" not in text:
        problems.append("LICENSE is not the MIT License")
    notices = [l for l in text.splitlines() if l.startswith("Copyright (c)")]
    if not any("Ahmii Labs" in l for l in notices):
        problems.append("LICENSE does not carry the Ahmii Labs copyright")
    if len(notices) < 2:
        problems.append("LICENSE must keep the earlier copyright notice as well")
    return problems


def check_headers(root):
    problems = []
    for path in walk(root):
        if path.endswith((".py", ".ts")):
            head = "\n".join(read(path).split("\n")[:6])
            if "SPDX-License-Identifier: MIT" not in head:
                problems.append("no license header: " + os.path.relpath(path, root))
            elif "Ahmii Labs" not in head:
                problems.append("no Ahmii Labs copyright: " + os.path.relpath(path, root))
    return problems


def check_skills(root):
    problems = []
    for name in sorted(os.listdir(root)):
        skill = os.path.join(root, name, "SKILL.md")
        if not os.path.isfile(skill):
            continue
        m = re.match(r"^---\n(.*?)\n---\n", read(skill), re.S)
        if not m:
            problems.append("%s: no frontmatter" % name)
            continue
        fm = m.group(1)
        if ("name: %s\n" % name) not in fm + "\n":
            problems.append("%s: frontmatter name does not match the folder" % name)
        if "description:" not in fm:
            problems.append("%s: no description" % name)
    return problems


def check_manifests(root):
    problems = []
    docs = {}
    for fn in ("plugin.json", "marketplace.json"):
        path = os.path.join(root, ".claude-plugin", fn)
        try:
            docs[fn] = json.loads(read(path))
        except (OSError, ValueError) as exc:
            problems.append("%s: %s" % (fn, exc))
    plugin = docs.get("plugin.json")
    market = docs.get("marketplace.json")
    if plugin:
        if plugin.get("license") != "MIT":
            problems.append("plugin.json: license is not MIT")
        if not plugin.get("version"):
            problems.append("plugin.json: no version")
    if plugin and market:
        entry = market["plugins"][0]
        if entry.get("version") != plugin.get("version"):
            problems.append("plugin.json and marketplace.json versions differ")
    return problems


def check_links(root):
    problems = []
    link = re.compile(r"\]\(([^)\s]+)\)")
    for path in walk(root):
        if not path.endswith(".md"):
            continue
        for target in link.findall(read(path)):
            if re.match(r"^(https?:|mailto:|#)", target):
                continue
            rel = target.split("#")[0]
            if rel and not os.path.exists(os.path.join(os.path.dirname(path), rel)):
                problems.append("%s: broken link %s" % (os.path.relpath(path, root), target))
    return problems


def check_dashes(root):
    bad = []
    for path in walk(root):
        if path.endswith((".md", ".py", ".json", ".ts", ".csv")) and EM_DASH in read(path):
            bad.append("em dash in " + os.path.relpath(path, root))
    return bad


CHECKS = (("license", check_license), ("headers", check_headers),
          ("skills", check_skills), ("manifests", check_manifests),
          ("links", check_links), ("dashes", check_dashes))


def run(root):
    return {name: fn(root) for name, fn in CHECKS}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Integrity check for the Replica pack.")
    ap.add_argument("root", nargs="?", default=os.path.dirname(os.path.abspath(__file__)))
    ap.add_argument("--json", action="store_true", help="print the results as JSON")
    args = ap.parse_args(argv)
    results = run(args.root)
    failed = sum(len(v) for v in results.values())
    if args.json:
        print(json.dumps({"ok": failed == 0, "problems": results}, indent=2))
    else:
        for name, problems in results.items():
            print("%-10s %s" % (name, "ok" if not problems else "%d problem(s)" % len(problems)))
            for p in problems:
                print("  - " + p)
        print("\nPack is clean." if not failed else "\n%d problem(s) found." % failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
