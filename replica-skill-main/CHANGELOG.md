# Changelog

## 1.2.0 - Use it as a Claude skill

- Added `build_skill.py`, which folds the eleven stages, six tools and the
  templates into one skill called `replica` and writes `dist/replica.zip`,
  ready to upload to Claude as a skill.
- Added `claude-skill/router.md`, the router SKILL.md that picks the stage and
  carries the rules that hold in every stage.
- Tool and template paths in the stage playbooks are rewritten for the single
  skill, and `/replica-<stage>` commands become plain stage names.
- Shipped the prebuilt skill at `releases/replica.zip`; a test keeps it in sync
  with the sources.
- Tests cover the built skill: layout, frontmatter limits, every referenced
  file, no stale paths, and the tools running from inside the build.

## 1.1.0 - Ahmii Labs edition

- Added `LICENSE` (MIT) with the Ahmii Labs copyright, keeping the earlier
  copyright notice the MIT License requires.
- Added `NOTICE.md` with the rights summary.
- Added an SPDX license and copyright header to every Python and TypeScript
  file.
- Added `check_pack.py`, a standard-library integrity check: license present,
  headers present, skill frontmatter valid, manifests consistent, markdown
  links resolve, no em dashes.
- Plugin and marketplace manifests now carry version 1.1.0, the MIT license
  field and Ahmii Labs as author and owner, and the repository at
  github.com/mrz3ron3x/replica-skill.
- Tests extended to cover the license, the headers, the manifests and
  `check_pack.py`.

## 1.0.0

- First release.
