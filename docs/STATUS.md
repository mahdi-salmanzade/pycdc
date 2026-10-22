# Status

**Current part:** 2 — Audit the implementation and establish the benchmark
**Status:** READY_FOR_REVIEW. The implementation and measurements are done.
Independent reproduction and review are pending, so this is not COMPLETE.
**Authorized next action:** hand `docs/HANDOFF.md` to the reviewing models.
Part 3 is **not** authorized until the user says "continue".

Part 1: COMPLETE (gate passed 2026-10-22).

## Part 2 gate checklist

| Gate item | State | Evidence |
| --- | --- | --- |
| Another model can reproduce the baseline from the recorded commands | **pending independent run** | `reports/part2-baseline/reproduce.sh` reproduced all 2,445 cases exactly in a fresh workroot (0 changes, 0 corpus drift). A Debug-build run was also identical. No other model has run it yet. |
| Reports distinguish every validation stage and outcome | done | `reports/part2-baseline/SUMMARY.md` and `FAILURES.md`: load / disassemble / decompile / syntax / behavior; PASS, FAIL, N/A, MISSING and HARNESS_ERROR; crash, timeout and incomplete counted separately; stage timings. |
| The harness catches deliberate semantic changes | done | `reports/part2-baseline/CONTROLS.md`: 29 negative controls, each detected on its declared channel at every live `-O` level (417 cases). Positive controls: 1,029/1,029 match. 0 unexpected outcomes. |
| The required feature scope is explicit | done, **review pending** | `harness/requirements.json` and `docs/FEATURE_MATRIX.md` assign all 73 fixtures to Parts 5–7, set Part 4's decoding scope and list the explicit exclusions. ASTRA has not reviewed the scope; Kimi K3 has not reviewed the fixtures. |
| Pipeline mapped from the real code | done | `docs/ARCHITECTURE.md`. Key claims were re-verified in the source or by execution. It was produced by an Opus sub-agent, so it is not an independent review. |
| Baseline frozen with hashes and exact commands | done | `reports/part2-baseline/README.md`: harness commit `afc5000`, fixture tree `d8caf220`, binary and interpreter hashes. |

## Baseline in one line

At upstream `b428976`, the feature corpus has 0 behavioral passes on
3.13/3.14 and 15/15/9 on 3.10/3.11/3.12. 3.14 fails at load and 3.13 at
decompile (`MAKE_FUNCTION`). There are 63 silent semantic mismatches and
9 crashes. The upstream token suite is unchanged (191 PASS / 39 XFAIL).
