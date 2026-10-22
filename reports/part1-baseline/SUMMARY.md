# Part 1 baseline — unmodified upstream build and existing checks

Measured on 2026-10-22 against upstream `zrax/pycdc` `master` at
`b4289760970dbc399684f1e155ec6d1ea1cc787e` ("Merge pull request #599 …",
538 commits). No source changes.

## Toolchain

| Item | Value |
| --- | --- |
| Host | macOS 26.7.1 (25G241), arm64, Xcode SDK 27.0 |
| C++ compiler | Apple clang 21.0.0 (clang-2100.3.34.2), `/usr/bin/c++` |
| CMake / generator | 4.4.4 / Unix Makefiles |
| git / gh | 2.54.0 (Apple Git-157) / 2.103.0 |
| Project flags | `-Wall -Wextra -Wno-error=shadow -Werror`, C++11 |
| Python chosen by CMake `FindPython3` for `check` | 3.15.0 (Homebrew), outside project scope; see notes |

Available CPython interpreters (`platform.python_version()`):

| Version | Path | Note |
| --- | --- | --- |
| 3.10 | — | **missing**: no 3.10 interpreter installed |
| 3.11.17 | `/opt/homebrew/opt/python@3.11/bin/python3.11` | |
| 3.12.2 | `~/.pyenv/versions/3.12.2/bin/python3.12` | pyenv default `python3` |
| 3.12.15 | `/opt/homebrew/bin/python3.12` | second 3.12, not used |
| 3.13.14 | `~/.local/bin/python3.13` (uv-managed) | |
| 3.14.9 | `/opt/homebrew/opt/python@3.14/bin/python3.14` | |
| 3.15.0 | `/opt/homebrew/bin/python3.15` | out of scope; used only for the documented `check` |

## Commands and results

```bash
cmake -S . -B build/debug   -DCMAKE_BUILD_TYPE=Debug     # exit 0
cmake --build build/debug -j8                            # exit 0, no warnings
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release   # exit 0
cmake --build build/release -j8                          # exit 0, no warnings
JOBS=8 cmake --build build/debug   --target check        # exit 0
JOBS=8 cmake --build build/release --target check        # exit 0
(cd build/debug && make check JOBS=4)                    # exit 0 (README form)
```

Upstream runner output (per test name, both builds): 93 test names, with
79 status lines reading `PASS (...)` and 14 reading `XFAIL (...)`. The runner
does not print XPASS and leaves the XFAIL count blank in mixed lines (see
`docs/DECISIONS.md` D-004).

Per-file classification with the identical pass criterion:

```bash
cd build/debug   # or build/release
python3.12 -I ../../reports/part1-baseline/per_file_outcomes.py --json out.json
```

| Build | token_dump interpreter | PASS | FAIL | XFAIL | XPASS | crash/timeout |
| --- | --- | --- | --- | --- | --- | --- |
| Debug | 3.11.17 | 191 | 0 | 39 | 0 | 0 / not measured |
| Debug | 3.12.2 | 191 | 0 | 39 | 0 | 0 / not measured |
| Debug | 3.13.14 | 191 | 0 | 39 | 0 | 0 / not measured |
| Debug | 3.14.9 | 191 | 0 | 39 | 0 | 0 / not measured |
| Debug | 3.15.0 | 191 | 0 | 39 | 0 | 0 / not measured |
| Release | 3.12.2 | 191 | 0 | 39 | 0 | 0 / not measured |

Per-file results are identical across all six runs (compared as JSON
`results` arrays). The canonical file is `per_file_outcomes.json` (Debug,
3.12.2). Every `.pyc` has a tokenized expectation and every expectation has at
least one `.pyc`. "Crash 0" means no run failed at the pycdc stage, which
includes nonzero exits. There is no timeout, so hangs would not be detected,
though none occurred and the whole suite takes about 2 s.

All 39 XFAIL files fail at the `token_mismatch` stage. A separate scan
(`build/release/pycdc tests/xfail/<f>.pyc`) found exit 0, empty stderr, and no
`incomplete`, `unsupported` or `warning` text in any of the 39 outputs.

Corpus identity: upstream `tests/` tree `ae59dd3b9546038d333d176982985900d5b075c0`.
SHA-256 of `tests/run_tests.py` is
`f7d524c94317401ff49e65218a78f64c870d29ac64aee84fa46172da678d9a94`; of
`scripts/token_dump`, `913d1e88fab77d9d5880904e14a191f5b7551c7615e0d03cdb87632a30540520`.

## Not run, or unavailable

- CodeQL and MSVC CI: not run locally (no Windows host). Upstream Linux CI was
  not run. Its workflow triggers on pushes to `master` and on PRs, so pushing
  `bootstrap` to the fork does not trigger it.
- Python 3.10 interpreter: missing. Upstream's check does not need it, because
  it uses committed `.pyc` files, but Part 2's compile-and-validate harness
  will.
- Isolation: the upstream fixtures are the project's own committed regression
  files. pycdc only parses them and nothing is executed. No sandbox or resource
  limits were applied in Part 1. Part 2 must add them before any untrusted
  input is parsed.

## Notes

- CMake's `FindPython3` picks the newest interpreter (3.15.0) for `check`.
  This did not change results here, but Part 2 should pin it
  (`-DPython3_EXECUTABLE=...`).
- Raw build and check logs were written to session scratch space and are not
  committed, under the raw-log policy in `AGENTS.md`.
