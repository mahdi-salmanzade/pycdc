# Part 2 frozen baseline (corpus v1)

This is the behavioral benchmark of **unmodified upstream pycdc**. Every later
change is compared against it with `harness/difftest.py compare`. Do not
regenerate it in place. A new baseline needs a recorded decision in
`docs/DECISIONS.md` and a new directory.

## Identity

| Item | Value |
| --- | --- |
| frozen | 2026-10-22T20:10Z |
| decompiler source | byte-identical to upstream `b4289760970dbc399684f1e155ec6d1ea1cc787e` (`git diff --stat b428976 HEAD` over sources, `bytes/`, `CMakeLists.txt`, `tests/`, `scripts/` is empty) |
| harness commit | `afc500098e2b7fe2c64e1ef4b821a931495b7f3f` (clean tree; `harness/` tree `ef26d7e148c219a01cc0b6a05daadb30af79afdd`) |
| fixture corpus v1 | `harness/fixtures` tree `d8caf220054279a8271861dacb246590944f2d24`: 73 fixtures |
| upstream corpus | `tests/` tree `ae59dd3b9546038d333d176982985900d5b075c0` (90 `tests/input` sources, used by the `upstream-inputs` suite) |
| interpreters | CPython 3.10.22 / 3.11.17 / 3.12.15 / 3.13.17 / 3.14.9 (uv python-build-standalone, macOS aarch64), magic 3439 / 3495 / 3531 / 3571 / 3627 |
| host | macOS 26.7.1 arm64, Apple clang 21.0.0, CMake 4.4.4, harness host Python 3.12.2 |
| binaries (Release) | `pycdc` sha256 `8c0e1d265da12bd37e266a88422e410ed380ce8643e53e935c06897b94a8b2f0`, `pycdas` `9c113e5bba7a4c520f1cf4a52e84cfdd47d460d46c3ebd5a48485ca23163df33`, `libpycxx.a` `582e0e49feb6a641a4e07532e0a9c89b1bad87f1bdb94a11a78067c34c80fbf3` |
| isolation | `macos-sandbox-exec` (D-007) |

Every case in `baseline.json` records the SHA-256 of its fixture source, of
the compiled `.pyc` and of the recovered source. `compare` reports any `.pyc`
hash change as `corpus_drift`.

## Files

| File | Content |
| --- | --- |
| `baseline.json` | 2,445 cases: `features` 73 × 5 versions × 3 `-O` levels, and `upstream-inputs` 90 × 5 × 3. One JSON line per case, with every stage's status, kind, cause and time |
| `SUMMARY.md` | per-version outcome table by stage, plus tables by category, by `-O` level, by stage timing, and by top failure causes |
| `FAILURES.md` | failure manifest: every cause per stage, every crash, every silent semantic mismatch with its first observed difference |
| `controls.json`, `CONTROLS.md` | harness validation: 1,029 positive and 432 negative control cases |
| `opcode_coverage.md`, `.json` | `bytes/` tables and `ASTree.cpp` cases versus each interpreter's `dis.opmap`, and corpus opcode usage |
| `upstream_per_file_outcomes.json` | upstream token-level suite, per file, for the same build |
| `GATES.md` | `difftest.py gate --part 4..7` dry runs: the distance to each gate |
| `reproduce.sh` | one-command reproduction and comparison |

## Reproduce

```bash
harness/setup_interpreters.sh                  # once; needs network for the download
PYTHON=python3 reports/part2-baseline/reproduce.sh build/part2-repro
```

`reproduce.sh` was run independently after the freeze. All 2,445 cases came
out identical (regression, failure_changed, missing_coverage, harness_error
and corpus_drift all 0) and controls reported 0 unexpected outcomes. A run
against the **Debug** build was also identical to this Release baseline.

The individual commands that produced these files (from the repository
root, with `R=reports/part2-baseline`):

```bash
python3 harness/difftest.py controls --out $R/controls.json --summary $R/CONTROLS.md
python3 harness/difftest.py run --suite features,upstream-inputs --out $R/baseline.json --summary $R/SUMMARY.md
python3 harness/tools/opcode_coverage.py --pyc-root build/difftest/features --out $R/opcode_coverage.md --json $R/opcode_coverage.json
(cd build/release && python3 -I ../../reports/part1-baseline/per_file_outcomes.py --json ../../$R/upstream_per_file_outcomes.json)
python3 harness/tools/failure_manifest.py $R/baseline.json > $R/FAILURES.md
python3 harness/difftest.py gate --part N --results $R/baseline.json --controls $R/controls.json --upstream $R/upstream_per_file_outcomes.json --limit 0
```

## Headline measurements

**Feature fixtures**, validated up to behavior. Each case is counted at its
earliest failing stage.

| Version | Cases | PASS | FAIL load | FAIL disassemble | FAIL decompile | FAIL syntax | FAIL behavior (silent) | of which crash | of which incomplete | N/A |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3.10 | 219 | 15 | 0 | 0 | 126 | 15 | 36 | 6 | 93 | 27 |
| 3.11 | 219 | 15 | 0 | 0 | 165 | 6 | 15 | 3 | 124 | 18 |
| 3.12 | 219 | 9 | 0 | 0 | 175 | 11 | 12 | 0 | 142 | 12 |
| 3.13 | 219 | 0 | 0 | 0 | 210 | 0 | 0 | 0 | 210 | 9 |
| 3.14 | 219 | 0 | 219 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

There were no timeouts, no MISSING interpreters and no HARNESS_ERROR.

**Upstream inputs**, compiled and decompiled up to syntax, never executed.

| Version | PASS (syntax) | FAIL decompile | FAIL syntax | FAIL load | N/A (not valid source for this version) |
| --- | --- | --- | --- | --- | --- |
| 3.10 | 135 | 21 | 9 | 0 | 105 |
| 3.11 | 114 | 42 | 9 | 0 | 105 |
| 3.12 | 120 | 33 | 12 | 0 | 105 |
| 3.13 | 66 | 90 | 9 | 0 | 105 |
| 3.14 | 0 | 0 | 0 | 165 | 105 |

The upstream-inputs decompile failures include 3 crashes (`test_with`, 3.11).

**Classification** (details in `FAILURES.md`):

- **3.14:** every file fails at load with `Bad MAGIC!`. There is no 3.14
  magic and no opcode table.
- **3.13:** every applicable fixture (210 cases) is incomplete at decompile.
  - 204 of them stop at `Unsupported opcode: MAKE_FUNCTION`, the 3.13
    no-argument form.
  - The rest stop at `CALL_INTRINSIC_1`, `CALL_KW` and similar.
  - 3.13 loads and disassembles cleanly.
- **3.10–3.12 decompile** (feature suite), most frequent causes first:
  - unhandled `MAKE_CELL` (96 cases);
  - `RETURN_GENERATOR` (51);
  - `JUMP_IF_NOT_EXC_MATCH` (35);
  - `CALL_FUNCTION_EX` (24);
  - `Stack history is not empty!` and `Something TERRIBLE happened!`
    diagnostics (21 each);
  - `Unsupported argument found for LIST_EXTEND` errors (18);
  - `UNPACK_EX` (12).
- A mid-run `std::exit` on `PycBuffer` end of stream accounts for 6 cases
  (3.10).
- **Crashes:** 9 SIGSEGVs in `with` statements (3.10, 3.11), plus 3 in
  upstream `test_with` (3.11).
- **Silent semantic mismatches:** 63 cases where pycdc exited 0 with no
  diagnostic and the output compiled, but behaved differently. Root-cause
  evidence is in `docs/ARCHITECTURE.md`. Examples:
  - wrong function defaults (`bucket = ([],)`);
  - dropped keyword-only defaults;
  - fake `self = None` defaults on closures;
  - `import os.path` emitted as `import os.path as os`;
  - lost `except … as e`;
  - `and`/`or`/conditional expressions turned into statements, which
    changes evaluation order.
- **Marked output:** none of the 414 outputs marked incomplete or with
  diagnostics behaved correctly when executed.

**Harness validation:**

- Positive controls: 1,029 of 1,029 match.
- Negative controls: all 29 mutations were detected on their declared channel
  at every live level (417 cases). The 15 dead-level cases (asserts at
  `-O`/`-OO`, a docstring at `-OO`) matched as expected.
- 0 unexpected outcomes in total.

**Opcode audit:**

- For 3.10–3.13, pycdc's opcode tables agree with CPython on every opcode it
  can write to disk.
- The AST builder lacks cases for 20, 28, 32 and 41 opcodes respectively that
  the corpus uses.
- 3.14 has no table.
- The corpus emits every exec-mode-emittable opcode of every version. The
  exceptions are `PRINT_EXPR` (interactive only) and runtime-internal
  opcodes.
