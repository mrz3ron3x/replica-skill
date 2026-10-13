#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Ahmii Labs. See LICENSE.
"""Build the Replica pack into one Claude skill you can upload as a zip.

Claude takes one skill per zip, so this folds the eleven stage playbooks, the
six tools and the templates into a single skill called `replica`: a router
SKILL.md, references/, scripts/ and assets/. Standard library only.

    python3 build_skill.py                 # writes dist/replica/ and dist/replica.zip
    python3 build_skill.py --out /tmp/out

Then in Claude, upload dist/replica.zip as a skill. In Claude Code, copy
dist/replica/ into ~/.claude/skills/.
"""

import argparse
import json
import os
import re
import shutil
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
NAME = "replica"
STAGES = ("recon", "architect", "design", "build", "backend", "test", "diff",
          "entrepreneur", "brand", "launch", "deploy")
TOOLS = (("replica-brand", "sweep.py"), ("replica-design", "contrast.py"),
         ("replica-diff", "imgdiff.py"), ("replica-diff", "parity.py"),
         ("replica-entrepreneur", "reviews.py"), ("replica-launch", "listing.py"),
         ("replica-entrepreneur", "themes.json"))
ASSETS = (("replica-recon", "recon-map.md"), ("replica-recon", "features.csv"),
          ("replica-architect", "architecture.md"), ("replica-design", "tokens.json"),
          ("replica-test", "test-plan.md"), ("replica-test", "bug-report.md"),
          ("replica-test", "e2e.example.spec.ts"), ("replica-launch", "listing.example.json"),
          ("replica-deploy", "preflight.md"))
FIXED_TIME = (2026, 1, 1, 0, 0, 0)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def strip_frontmatter(text):
    return re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.S).lstrip("\n")


def convert(body):
    """Rewrite a stage playbook so its paths work inside the single skill."""
    tools = "|".join(t.split(".")[0] for _, t in TOOLS if t.endswith(".py"))
    body = re.sub(r"python3 (?:\.\./replica-[a-z]+/)?(%s)\.py" % tools,
                  r"python3 scripts/\1.py", body)
    body = re.sub(r"\(Paths are relative to wherever the pack is installed\..*?on\.\)",
                  "(Tool paths such as `scripts/parity.py` are relative to this skill's "
                  "folder, not to your project.)", body, flags=re.S)
    body = body.replace("(`themes.json`,", "(`scripts/themes.json`,")
    body = re.sub(r"([Tt]ools? in )this folder", r"\1`scripts/`", body)
    body = re.sub(r"in\s+this folder", "in `assets/`", body)
    body = re.sub(r"`/replica-([a-z]+)`", r"the `\1` stage", body)
    body = re.sub(r"/replica-([a-z]+)", r"the `\1` stage", body)
    return body


def version():
    with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as fh:
        return json.load(fh)["version"]


def build_folder(out):
    """Write the skill folder and return its path."""
    folder = os.path.join(out, NAME)
    if os.path.isdir(folder):
        shutil.rmtree(folder)
    router = read(os.path.join(ROOT, "claude-skill", "router.md"))
    write(os.path.join(folder, "SKILL.md"), router.replace("{{version}}", version()))
    write(os.path.join(folder, "LICENSE"), read(os.path.join(ROOT, "LICENSE")))
    for stage in STAGES:
        src = os.path.join(ROOT, "replica-" + stage, "SKILL.md")
        write(os.path.join(folder, "references", stage + ".md"),
              convert(strip_frontmatter(read(src))))
    for sub, files in (("scripts", TOOLS), ("assets", ASSETS)):
        for skill, fn in files:
            write(os.path.join(folder, sub, fn), read(os.path.join(ROOT, skill, fn)))
    return folder


def build_zip(folder, out):
    """Zip the skill folder with the folder itself at the top of the archive."""
    zpath = os.path.join(out, NAME + ".zip")
    if os.path.exists(zpath):
        os.remove(zpath)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(folder):
            dirnames.sort()
            for fn in sorted(filenames):
                full = os.path.join(dirpath, fn)
                arc = os.path.join(NAME, os.path.relpath(full, folder)).replace(os.sep, "/")
                info = zipfile.ZipInfo(arc, FIXED_TIME)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (0o755 if fn.endswith(".py") else 0o644) << 16
                with open(full, "rb") as fh:
                    zf.writestr(info, fh.read())
    return zpath


def main(argv=None):
    ap = argparse.ArgumentParser(description="Build the Replica pack as one Claude skill.")
    ap.add_argument("--out", default=os.path.join(ROOT, "dist"))
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)
    folder = build_folder(args.out)
    zpath = build_zip(folder, args.out)
    count = sum(len(f) for _, _, f in os.walk(folder))
    print("Built %s (%d files)" % (folder, count))
    print("Upload this to Claude as a skill: %s" % zpath)
    return 0


if __name__ == "__main__":
    sys.exit(main())
