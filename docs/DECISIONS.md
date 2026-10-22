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

## D-006 — Pinned interpreters in an isolated uv directory (2026-10-22, Part 2)

**Context.** The roadmap needs exact CPython versions for compiling and
validating. The host had a mix of pyenv, Homebrew and uv interpreters. 3.10
was missing, and there were two different 3.12 builds.

**Decision.** Pin 3.10.22, 3.11.17, 3.12.15, 3.13.17 and 3.14.9, the latest
uv-provided patch releases on 2026-10-22 (`harness/interpreters.json`).
- They are installed with `uv python install --no-bin` into
  `~/.cache/pycdc-harness/python`.
- The user's `~/.local/bin` links and uv's per-minor links stay untouched.
- The harness verifies the exact version and the `.pyc` magic before every run.

**Consequence.** Another machine gets byte-identical `.pyc` files from the same
builds; two independent runs gave no corpus drift. A version bump is a
recorded decision, and the baseline must be re-frozen with it.

## D-007 — Harness isolation: sandbox-exec, scrubbed environment, rlimits (2026-10-22, Part 2)

**Decision.** Every process the harness starts runs through
`harness/sandbox.py`, with:
- a macOS `sandbox-exec` profile: no network, writes only to the case
  directory, no reads under `$HOME` except the interpreters and the repo;
- a scrubbed environment;
- CPU and file-size limits and a wall-clock timeout.

The profile was verified by probes. Network connect and DNS were denied.
Writes to `/tmp`, `$HOME` and the repo were denied. Reads of `~/.ssh`,
`~/.config/gh`, `~/.gitconfig` and Keychains were denied.

**Consequence.**
- Only macOS has full isolation. Other platforms need an explicit
  `--sandbox none --allow-unisolated`, which is recorded in the results.
- Linux isolation is part of Part 8 CI.
- macOS does not enforce `RLIMIT_AS`.

## D-008 — Behavioral observation contract (2026-10-22, Part 2)

**Decision.** Behavior is compared through the channels in `harness/README.md`:
- module and `observe()` transcripts, which preserve stdout/stderr
  interleaving;
- return values and exceptions, described structurally, including
  cause/context/notes/groups;
- a structural snapshot of module globals, including class dicts with dunder
  methods and function parameter lists with defaults;
- a deterministic finalization step (automatic GC disabled, explicit
  `gc.collect()`);
- the process's exit-time output.

The reference is the **compiled `.pyc` executed at its own optimization
level**, not the original source.

**Consequence.**
- The exclusions are explicit: line numbers, code attributes, identity,
  compile-time warnings and timing.
- The contract was validated by 29 negative controls, all detected on their
  declared channel, and by positive controls with 0 false positives.
- The `default_value` control first exposed a real gap: dunder methods were
  excluded from class descriptions. The fix is in `observe.py`
  (`IMPLICIT_CLASS_ATTRS`).

## D-009 — Earliest-stage attribution with a separate load probe (2026-10-22, Part 2)

**Context.** pycdas does not check `isValid()`, exits 0 after `Bad MAGIC!`,
and loses buffered stdout when it crashes. A load failure could therefore be
misattributed to disassembly.

**Decision.** The load stage uses `harness/tools/load_probe.cpp`, linked
against the unmodified `libpycxx.a` of the build under test. It runs only
`PycModule::loadFromFile`.

Each case is classified at its earliest failing stage: load, disassemble,
decompile, syntax, behavior. Output that is incomplete or has diagnostics is
still executed for information, but never counts as PASS.

## D-010 — Fixtures assigned to the highest part whose constructs they use (2026-10-22, Part 2)

**Context.** The first fixture draft mixed constructs: "Part 5" fixtures used
`try`/loops/comprehensions. Their gates could then only pass after Part 6/7
work, or by weakening.

**Decision.**
- Part 5 fixtures use no Part 6/7 constructs, and Part 6 fixtures no Part 7
  ones. Content was moved or split to achieve this; nothing was deleted.
- `harness/requirements.json` maps all 73 fixtures and is checked by
  `difftest.py gate`.
- Required-to-pass versions are 3.13 and 3.14. For 3.10–3.12 the requirement
  is no regression.
- These are proposals for ASTRA to review. Once reviewed they may only be
  tightened.

## D-011 — Part 2 continues on `bootstrap` (2026-10-22, Part 2)

**Decision.** Part 2 work is committed on `bootstrap`, which now serves as the
project's integration branch. Fork `master` stays equal to upstream `master`
(D-003). Isolated candidate branches/worktrees remain reserved for Part 3.

## D-012 — Executing only authored fixtures (2026-10-22, Part 2)

**Decision.**
- Behavioral execution is limited to `harness/fixtures`, written for this
  project and reviewed by reading before execution. Independent review by
  Kimi K3 is pending.
- Upstream's `tests/input` sources are compiled and decompiled but never run.
- No `.pyc` from outside the project is parsed in Part 2.
