# Handoff

Written by Opus, the Part 1 implementation owner, at the end of Part 1. Before
acting, read `AGENTS.md` and `docs/STATUS.md`, and check the repository itself.

## Repository state

| Item | Value |
| --- | --- |
| Local checkout | `/Users/intzero/Documents/pycdc/pycdc` |
| Fork | https://github.com/mahdi-salmanzade/pycdc (owner `mahdi-salmanzade`, parent `zrax/pycdc`) |
| Branch | `bootstrap` (created from `b428976`; tracks `origin/bootstrap`) |
| Starting commit | `b4289760970dbc399684f1e155ec6d1ea1cc787e` = upstream `master` = fork `master` |
| Bootstrap commit | `cb321f8c59b428f490584d7316387c65870fd02f`, pushed and verified on `origin/bootstrap` |
| Checkpoint tip | the commit after `cb321f8`, which records this verification; check it with `git ls-remote origin refs/heads/bootstrap` |
| Dirty tree | none; `build/` is gitignored |

## Completed work (Part 1)

- Verified `gh` auth (account `mahdi-salmanzade`, keyring token, scopes
  include `repo`). No token was printed.
- Confirmed that no fork existed, then created one with
  `gh repo fork zrax/pycdc --clone=false`.
- Reused the verified clean upstream clone and rewired its remotes (D-001,
  D-002).
- Built Debug and Release, and ran the documented `check` target plus a
  per-file classification (D-004).
- Wrote `AGENTS.md`, `docs/{ROADMAP,STATUS,HANDOFF,COMPATIBILITY,DECISIONS}.md`
  and `reports/part1-baseline/`.

No decompiler source was changed and no outside contributions were merged.

## Reproduce

```bash
cd /Users/intzero/Documents/pycdc/pycdc
git fetch origin upstream && git switch bootstrap
git rev-parse upstream/master            # expect b4289760970dbc399684f1e155ec6d1ea1cc787e
cmake -S . -B build/debug -DCMAKE_BUILD_TYPE=Debug && cmake --build build/debug -j8
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release && cmake --build build/release -j8
JOBS=8 cmake --build build/debug --target check          # expect exit 0
cd build/debug && python3.12 -I ../../reports/part1-baseline/per_file_outcomes.py
# expect: PASS=191, FAIL=0, XFAIL=39, XPASS=0; all 39 XFAIL at stage token_mismatch
```

## Measured results

See `reports/part1-baseline/SUMMARY.md` and `per_file_outcomes.json`. The
results are identical for Debug and Release and with `token_dump` under CPython
3.11.17, 3.12.2, 3.13.14, 3.14.9 and 3.15.0.

## Review status

No other model has reviewed anything. No production code changed in Part 1.
`reports/part1-baseline/per_file_outcomes.py` is unreviewed measurement
tooling. The investigator role (Kimi K3) may want to check it, and it is
superseded by the Part 2 harness.

## Unresolved questions for Part 2

1. **Pinned interpreters.** 3.10 is missing. There are two 3.12 builds (3.12.2
   pyenv, 3.12.15 Homebrew). Proposal: pin exact patch versions via
   `uv python install` (which needs network access to download, a one-time
   setup step) and record them in the harness config.
2. **Isolation for parsing untrusted `.pyc`.** Candidates on this host:
   `sandbox-exec` (present), Docker CLI with colima (present, daemon not
   verified running), and `timeout`/rlimits. A choice is needed before any
   non-fixture input is parsed.
3. **CMake `check` interpreter.** `FindPython3` selects 3.15.0, which is out of
   scope. Pin it with `-DPython3_EXECUTABLE`.
4. **Silent XFAIL output.** All 39 XFAIL outputs carry no incomplete marker.
   Part 2 should check whether any of them are semantically wrong, which would
   matter for the "explicit unsupported reconstruction" rule.

## Next authorized action

Wait for the user to say "continue". Only then begin Part 2 (audit and
benchmark) as defined in `docs/ROADMAP.md`.
