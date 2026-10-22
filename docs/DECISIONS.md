# Decisions

Each decision records its context, the choice, and its consequences.
Supersede a decision with a new entry rather than editing an old one.

## D-001 — Reuse the existing local clone as the working repository (2026-10-22, Part 1)

**Context.** `/Users/intzero/Documents/pycdc/pycdc` already existed as a clone
of `https://github.com/zrax/pycdc.git`. Its state was verified before reuse:
`master` at `b4289760970dbc399684f1e155ec6d1ea1cc787e` (equal to upstream HEAD),
clean working tree, no stash, no untracked or ignored files, and
`git fsck --connectivity-only` reported no problems. The documented
`gh repo fork --clone` workflow would have collided with this directory.

**Decision.** Create the fork without cloning (`gh repo fork zrax/pycdc
--clone=false`). Then rewire this clone's remotes by hand instead of cloning a
second copy.

**Consequence.** One checkout, with verified history and no overwritten
directory.

## D-002 — Remote layout and write safety (2026-10-22, Part 1)

**Decision.**
- `origin` = `https://github.com/mahdi-salmanzade/pycdc.git` (fork, push target).
- `upstream` = `https://github.com/zrax/pycdc.git` for fetch. Its push URL is
  set to the invalid `DISABLED_no_push_to_upstream`, so an accidental push fails
  locally. (The account also has no push permission on `zrax/pycdc`.)
- `gh repo set-default mahdi-salmanzade/pycdc`, so `gh` operations without
  `--repo` target the fork and not upstream.
- The upstream default branch is discovered, not hardcoded:
  `git ls-remote --symref upstream HEAD` and `git remote set-head upstream --auto`.
  Both report `master`.

## D-003 — Project branches, overriding the global "commit to main" rule (2026-10-22, Part 1)

**Context.** The user's global instructions (`~/.claude/CLAUDE.md`, and
`~/AGENTS.md` for Codex) say never create branches and always commit and push
to `main`. The project prompt says to create a dedicated bootstrap branch and
push it to the fork. The fork has no `main`. Its default branch is `master`.

**Decision.** The user was asked and chose the project-prompt workflow on
2026-10-22. Bootstrap work goes on branch `bootstrap`, created from
`b428976` and pushed to `origin` only. Fork `master` stays identical to
upstream `master`. For this repository the project prompt overrides the global
no-branch rule.

**Consequence.** Upstream sync stays a fast-forward of fork `master`. Later
parts that need isolated candidates (Part 3) may use branches or worktrees as
the roadmap describes. The global rule that commit messages carry no model
co-author trailer still applies.

## D-004 — Part 1 baseline: wrap the upstream runner instead of modifying it (2026-10-22, Part 1)

**Context.** `tests/run_tests.py` reports per test name and never prints XPASS
(it computes `upass` but discards it). The XFAIL count in its
`PASS (n) + XFAIL ()` line is blank, and it has no timeout. Part 1 must not
change behavior, and the project rules require PASS, FAIL, XFAIL and XPASS to
be reported separately.

**Decision.** Add `reports/part1-baseline/per_file_outcomes.py`, a read-only
wrapper that imports `run_tests.decompyle_one` (the identical pass criterion)
and classifies each `.pyc` file separately. Upstream's runner and fixtures are
untouched.

**Consequence.** This is measurement tooling, not production code. It has not
been reviewed by another model. Part 2's harness replaces it. Fixing the
upstream runner's reporting is a candidate for a small upstream contribution
later.

## D-005 — Build directories (2026-10-22, Part 1)

**Decision.** Out-of-tree builds go in `build/debug` and `build/release`,
which are covered by the existing `build/` entry in `.gitignore`. Upstream CI
uses `build-debug`/`build-release`, which are not ignored, so they are avoided
locally.
