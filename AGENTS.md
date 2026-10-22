# AGENTS.md — working rules for this fork of pycdc

This file is for any agent or model working in this repository. Upstream
pycdc had no AGENTS.md at the fork point (`b428976`). Extend this file
carefully. Do not drop existing rules.

## Start of every session

1. Read `docs/STATUS.md`, `docs/HANDOFF.md` and `docs/ROADMAP.md`.
2. Check the actual repository: `git status --short --branch`, `git remote -v`,
   `git log --oneline -5`, `git fetch origin upstream`. Conversation memory
   is not the source of truth. These files and the repository are.
3. Work only on the part that `docs/STATUS.md` marks as authorized. Do not
   begin the next part until its predecessor's completion gate has passed and
   the user has said "continue".

## Mission (summary)

Reconstruct readable, behaviorally equivalent Python source from CPython `.pyc`
files. The initial focus is 3.13 and 3.14. Keep regression coverage for 3.10–3.12
and upstream's older-version tests. The tool must stay deterministic and local,
with no AI service, network or API keys needed to decompile. Exact comments and
formatting, native binaries (Cython/Nuitka), packaging extraction and
deobfuscation are out of scope. Do not silently expand to newer Python versions.

## Roles

| Role | Initial owner | Responsibility |
| --- | --- | --- |
| Coordinator / architecture | ASTRA | roadmap, scoping, architectural decisions, gate checks |
| Investigator / adversarial tests | Kimi K3 | CPython version research, failure minimization, fixtures, challenging assumptions |
| Implementation | Opus | focused patches, integration, implementation notes |

Roles can rotate. A model other than its author must review every
production-code patch, with concrete counterexamples and test evidence. If a
model cannot actually invoke another model, it must not simulate one or claim
a review happened. It writes a handoff in `docs/HANDOFF.md` instead. A patch
awaiting review is `READY_FOR_REVIEW`, not `COMPLETE`.

## Git workflow for this repository

- `origin` is the fork `mahdi-salmanzade/pycdc`. `upstream` is `zrax/pycdc`,
  fetch-only. Its push URL is deliberately set to `DISABLED_no_push_to_upstream`.
- The `gh` default repository is pinned to `mahdi-salmanzade/pycdc`
  (`gh repo set-default --view`). Pass `--repo mahdi-salmanzade/pycdc` explicitly
  on any `gh` write operation anyway.
- **Branching exception (approved by the user on 2026-10-22):** the user's
  global rule says "never create a branch; commit and push to main". For this
  repository the project prompt overrides it. Work happens on project branches
  such as `bootstrap`, and fork `master` is kept identical to upstream `master`.
  See `docs/DECISIONS.md` D-003.
- Pushing to the fork (`origin`) is authorized. Never force-push, rewrite
  shared history, delete repositories, or discard unrelated changes.
  Opening upstream PRs and publishing releases need explicit user approval.
- Do not add `Co-Authored-By` trailers for any model to commit messages.

## Engineering rules

- Inspect before modifying. Verify claims against source, the CPython
  documentation for the matching version, or executable tests. Record exact
  commit hashes and interpreter versions. Never invent test results, command
  output, supported versions or a successful push.
- Keep changes narrow. A wholesale rewrite needs a documented architectural
  limitation and a prototype that shows why incremental change is insufficient.
- Never fix tests by removing cases, weakening assertions, adding silent skips,
  or relabeling regressions as expected failures. Report PASS, FAIL, XFAIL,
  XPASS, SKIP, crash and timeout separately. A missing interpreter means
  missing coverage, not success.
- Unsupported reconstruction must be explicit. Do not delete instructions,
  replace code with `pass` or `...`, swallow exceptions, or emit plausible but
  invented logic. Mark partial output as incomplete and never count it as a
  successful decompilation.
- Never run unknown `.pyc` files, import unknown modules, or execute issue
  attachments. Parse untrusted inputs only in an isolated, resource-limited
  environment. Behavioral tests may execute only authored, reviewed fixtures in
  disposable workers without credentials or network access.
- Preserve upstream license notices (GPL-3.0, `LICENSE`) and contributor
  attribution.
- Keep large generated binaries and raw logs out of Git. The exception is small
  regression fixtures that are added deliberately. Reproducible summaries and
  failure manifests go under `reports/`.

## Build and test (unchanged upstream workflow)

```bash
cmake -S . -B build/debug   -DCMAKE_BUILD_TYPE=Debug
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release
cmake --build build/debug -j8 && cmake --build build/release -j8
cmake --build build/debug --target check        # == (cd build/debug && make check JOBS=4)
# per-file PASS/FAIL/XFAIL/XPASS (the upstream runner hides XPASS):
(cd build/debug && python3.12 -I ../../reports/part1-baseline/per_file_outcomes.py)
```

`build/` is gitignored. The upstream runner `tests/run_tests.py` runs
`scripts/token_dump` under whichever interpreter CMake's `FindPython3` selects.
Pass `-DPython3_EXECUTABLE=...` to pin it.

## Project-state files

| File | Purpose |
| --- | --- |
| `AGENTS.md` | working rules (this file) |
| `docs/ROADMAP.md` | parts 1–8 and their acceptance criteria |
| `docs/STATUS.md` | current checkpoint and gate state |
| `docs/HANDOFF.md` | what the next model needs: branch, commit, tree state, commands, results, open questions, next authorized action |
| `docs/COMPATIBILITY.md` | measured support only |
| `docs/DECISIONS.md` | architectural and process decisions |
| `reports/` | reproducible benchmark summaries and failure manifests |

Update `docs/STATUS.md` and `docs/HANDOFF.md` before stopping at any
checkpoint.
