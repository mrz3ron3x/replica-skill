---
name: replica
description: >-
  Clones the features and flows of any app, clean-room: reverse-engineers it
  into a recon map, plans the stack, rebuilds the design system and screens,
  adds the backend, tests it, scores parity against the original, mines real
  user reviews for what they hate, rebrands, writes the landing page and store
  listing, and ships it. Eleven stages with six built-in checking tools. Use
  whenever the user wants to clone, copy, replicate, reverse-engineer or
  rebuild an app or SaaS product, says "make my own version of X" or "like X
  but cheaper", pastes an app URL or App Store link to rebuild, asks what users
  hate about an app, wants a parity score, a rebrand sweep or a store listing
  check, or mentions replica, recon map or the Entrepreneur, even if they do
  not name a stage.
license: MIT
compatibility: Python 3.8+ for the tools (standard library only). Node and Playwright are only needed on the user's own machine for the test and deploy stages.
---

# Replica

Eleven stages that clone what an app does (features and flows), never what it
owns. Pack version {{version}}, by Ahmii Labs.

## How this skill is laid out

- `references/<stage>.md` is the full playbook for each stage. Read the one you
  need, not all eleven.
- `scripts/` holds six standard-library Python tools. Paths like
  `scripts/parity.py` in the playbooks are relative to this skill's folder, so
  call them by the full path this folder was loaded from. Run them from the
  user's project folder.
- `assets/` holds the templates (recon map, feature matrix, architecture,
  design tokens, test plan, bug report, e2e spec, listing, deploy preflight).
- The user's own work lives in a `replica/` folder in their project. Each stage
  reads what the stage before it wrote there. In a playbook, `replica-<stage>`
  means `references/<stage>.md`.

## The pipeline

recon, architect, design, build, backend, test, diff, entrepreneur, brand,
launch, deploy. Run them in that order, or any one on its own.

| stage | read | tool or template | writes in `replica/` |
| --- | --- | --- | --- |
| recon | `references/recon.md` | `assets/recon-map.md`, `assets/features.csv` | `recon.md`, `features.csv` |
| architect | `references/architect.md` | `assets/architecture.md` | `architecture.md`, `schema.sql` |
| design | `references/design.md` | `scripts/contrast.py`, `assets/tokens.json` | `design/` |
| build | `references/build.md` | none | the app, `clone-screens/` |
| backend | `references/backend.md` | none | migrations, server code |
| test | `references/test.md` | `assets/test-plan.md`, `assets/bug-report.md`, `assets/e2e.example.spec.ts` | `test-plan.md`, `bugs.md`, `e2e/` |
| diff | `references/diff.md` | `scripts/parity.py`, `scripts/imgdiff.py` | `parity.md`, `diffs/` |
| entrepreneur | `references/entrepreneur.md` | `scripts/reviews.py`, `scripts/themes.json` | `reviews.csv`, `feedback.md`, `fixes.md` |
| brand | `references/brand.md` | `scripts/sweep.py` | `brand.md`, `brand.json` |
| launch | `references/launch.md` | `scripts/listing.py`, `assets/listing.example.json` | `launch/` |
| deploy | `references/deploy.md` | `assets/preflight.md` | `deploy.md` |

## Picking the stage

1. Look at what is already in the user's `replica/` folder. The newest file
   tells you where they are, and the stage after it is the next one.
2. A pasted URL or App Store link and "clone this" means start at recon.
3. "Should I clone this?" or "what do users hate about X?" means run
   entrepreneur on its own first. It is a good way to decide before building.
4. A stage whose input file is missing stops and says which earlier stage to
   run. Do not invent the missing input.
5. Say which stage you are running and read its reference file before you start.

## Rules that hold in every stage

- **Clean-room.** Study what the app does and how people move through it, then
  write everything fresh. Never copy the target's source code, proprietary
  assets, logos, trademarks, copy or private APIs.
- **Only read what the user is allowed to read.** Public pages, store listings,
  help docs and the user's own account. Never scrape behind a login, never use
  someone else's account, never get past a paywall. If the user's account terms
  forbid building a competitor with it, say so and stay on public sources.
- **Always rebrand before launch.** New name, palette, logo and words. The
  brand sweep must exit clean before launch and deploy.
- **Nothing made up.** No invented reviews, quotes or numbers. Every claim from
  the Entrepreneur has a link and a stated sample size.
- **The user does the account steps.** Claude never buys a domain, types a
  password, enters a card or pastes a live key. Nothing goes live without the
  user's go.
- **Honest scope.** "Clone any app" means features and flow, not content, a
  network or licences the app owns. Size the job in recon before building.
- Not legal advice. Remind the user to run the trademark checks the brand stage
  lists and to talk to a lawyer before launch if money is at stake.

## Working in a chat

- If web search or fetch tools exist, use them for the public-page research in
  recon and entrepreneur, and cite the URL of every source.
- If code execution is available, run the tools directly and show their output.
  If not, give the user the exact commands to run themselves.
- Playwright tests, production builds and deploys run on the user's machine.
  Write the files and the commands, and let the user run them.
- Keep each stage's output in the file the playbook names, and finish with the
  short summary and the next stage the playbook asks for.

Licensed MIT. See `LICENSE`.
