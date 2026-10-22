# Compatibility — measured support only

This file records only what has been measured, and the level at which it was
measured. Absence from this file means **unmeasured**, not supported.

## Measurement levels

| Level | Meaning | Status |
| --- | --- | --- |
| L0 token match | pycdc exits 0 with no diagnostics, and `scripts/token_dump` of its output equals the committed expectation in `tests/tokenized/` | measured (Part 1) |
| L1 recompiles | recovered source compiles under the matching CPython | measured (Part 2) |
| L2 behavioral | differential execution against the compiled `.pyc` under the observation contract in `harness/README.md` | measured (Part 2), feature fixtures only |

L0 is upstream's existing regression criterion. It shows output stability
against expectations a human approved. It does **not** establish behavioral
equivalence.

## Baseline at upstream `b4289760970dbc399684f1e155ec6d1ea1cc787e` (Part 1, 2026-10-22)

Corpus: upstream `tests/`, git tree `ae59dd3b9546038d333d176982985900d5b075c0`,
230 `.pyc` files (191 in `tests/compiled`, 39 in `tests/xfail`). Results are
identical for the Debug and Release builds, and with `token_dump` run under
CPython 3.11.17, 3.12.2, 3.13.14, 3.14.9 and 3.15.0. Evidence:
`reports/part1-baseline/`.

| Fixture version | PASS | FAIL | XFAIL | XPASS |
| --- | --- | --- | --- | --- |
| 1.0 | 2 | 0 | 0 | 0 |
| 1.1 | 1 | 0 | 0 | 0 |
| 1.2 | 1 | 0 | 0 | 0 |
| 1.3 | 1 | 0 | 0 | 0 |
| 1.4 | 1 | 0 | 0 | 0 |
| 1.5 | 19 | 0 | 7 | 0 |
| 1.6 | 1 | 0 | 0 | 0 |
| 2.0 | 1 | 0 | 0 | 0 |
| 2.1 | 1 | 0 | 0 | 0 |
| 2.2 | 30 | 0 | 10 | 0 |
| 2.3 | 1 | 0 | 0 | 0 |
| 2.4 | 1 | 0 | 0 | 0 |
| 2.5 | 29 | 0 | 11 | 0 |
| 2.6 | 6 | 0 | 0 | 0 |
| 2.7 | 21 | 0 | 4 | 0 |
| 3.0 | 6 | 0 | 1 | 0 |
| 3.1 | 4 | 0 | 0 | 0 |
| 3.2 | 1 | 0 | 0 | 0 |
| 3.3 | 5 | 0 | 1 | 0 |
| 3.4 | 4 | 0 | 1 | 0 |
| 3.5 | 7 | 0 | 1 | 0 |
| 3.6 | 1 | 0 | 0 | 0 |
| 3.7 | 14 | 0 | 3 | 0 |
| 3.8 | 5 | 0 | 0 | 0 |
| 3.9 | 8 | 0 | 0 | 0 |
| **3.10** | 6 | 0 | 0 | 0 |
| **3.11** | 8 | 0 | 0 | 0 |
| **3.12** | 6 | 0 | 0 | 0 |
| **3.13** | — | — | — | — |
| **3.14** | — | — | — | — |
| total | 191 | 0 | 39 | 0 |

Target-version fixtures in the upstream corpus:
- 3.10: `GEN_START`, `op_precedence`, `simple_const`, `test_calls`, `test_for_loop_py3.8`, `test_sets`
- 3.11: `binary_ops`, `simple_const`, `swap`, `test_calls`, `test_exception_match_py311`, `test_kwnames`, `test_pop_jump_forward_if_false`, `test_pop_jump_forward_if_true`
- 3.12: `binary_slice`, `simple_const`, `store_slice`, `test_integers_py3`, `test_loops3`, `test_raise_varargs`
- 3.13, 3.14: **no fixtures, so these versions are unmeasured.**

## Observations (not support claims)

- All 39 XFAIL files fail only at the token-comparison stage. pycdc exits 0,
  prints nothing to stderr, and writes no "incomplete", "unsupported" or
  "warning" marker into its output. Whether these outputs are semantically
  wrong or only differ cosmetically is **still unevaluated**. They are
  Python 1.5–3.7 bytecode, outside the Part 2 behavioral matrix (3.10–3.14),
  so they remain token-level only.
- At `b428976`, source reading (not execution) shows that `pyc_module.h`
  defines magic values up to `MAGIC_3_13` and `bytes/` has opcode tables up to
  `python_3_13.cpp`. Neither has a 3.14 entry. 3.14 handling has not been
  executed or tested.

## Behavioral baseline at upstream `b428976` (Part 2, 2026-10-22)

Measured with the differential harness on fixture corpus v1 (73 authored
fixtures, `harness/fixtures` tree `d8caf220`). Each fixture runs on every
pinned interpreter at `-O0`, `-O1` and `-O2`. Each case is counted at its
earliest failing stage. The evidence is `reports/part2-baseline/`.

**L2: the recovered source behaves like the compiled `.pyc`.**

| Version | Applicable cases | L2 PASS | First failure at load / disassemble / decompile / syntax / behavior |
| --- | --- | --- | --- |
| 3.10 | 192 | 15 | 0 / 0 / 126 / 15 / 36 |
| 3.11 | 201 | 15 | 0 / 0 / 165 / 6 / 15 |
| 3.12 | 207 | 9 | 0 / 0 / 175 / 11 / 12 |
| 3.13 | 210 | **0** | 0 / 0 / 210 / 0 / 0 |
| 3.14 | 219 | **0** | 219 / 0 / 0 / 0 / 0 |

**L1 on upstream `tests/input`:** compiled with each interpreter and
decompiled, but never executed.

| Version | Compilable sources × 3 `-O` levels | L1 PASS |
| --- | --- | --- |
| 3.10 | 165 | 135 |
| 3.11 | 165 | 114 |
| 3.12 | 165 | 120 |
| 3.13 | 165 | 66 |
| 3.14 | 165 | 0 (load fails) |

**What this means.**

- At this baseline, **no Python version is supported at the behavioral level**
  for the fixture corpus.
- The passing 3.10–3.12 cases are a few expression, function and import
  fixtures.
- **63 cases are silent semantic mismatches**: exit 0, no diagnostic, the
  output compiles, but the behavior is wrong. A syntactically valid result is
  therefore not evidence of a correct decompilation (`FAILURES.md`).

**Decoding level.**

- The pycdc opcode tables for 3.10–3.13 map every on-disk CPython opcode
  correctly (`reports/part2-baseline/opcode_coverage.md`).
- 3.14 has no magic number and no table. It also introduces marshal version 5
  with `slice` constants (type code `':'`, verified with 3.14.9), which pycdc
  cannot parse.
