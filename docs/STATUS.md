# Status

**Current part:** 3, evaluate existing upstream work.

**Status:** READY_FOR_REVIEW.
- The evaluation, the integration and the measurements are done.
- The adopted production commits need an independent review, so this is
  not COMPLETE.

**Authorized next action:**
- Hand `docs/HANDOFF.md` to the reviewing models.
- Part 4 is **not** authorized until the user says "continue".

**Earlier parts:**
- Part 1: COMPLETE (gate passed 2026-10-22).
- Part 2: READY_FOR_REVIEW. Its independent reproduction and review (Kimi
  K3, ASTRA) are still outstanding. The user said "continue" with that gate
  unpassed, so Part 3 started on the user's instruction (D-013). Part 3's
  measurements depend on the Part 2 baseline; if a Part 2 review changes it,
  re-run `reports/part3-candidates/reproduce.sh`.

## Part 3 gate checklist

| Gate item | State | Evidence |
| --- | --- | --- |
| A reproducible comparison report exists | done | `reports/part3-candidates/README.md` and `COMPARISON.md`. `reproduce.sh` rebuilds every candidate from its pinned head and regenerates every table. |
| The integration decision is justified | done, **review pending** | D-015. Adopt only the 3.14 decoding layer. Reject both PRs' AST changes, which add 162/60 silent mismatches, new crashes, hangs (#616) and behavior changes on 3.10–3.12; keep them as references for Parts 5–7. |
| Independent review is recorded | **pending** | No other model has reviewed the adopted commits `200a4cd` and `27ef3c6` or the evaluation. |
| The selected foundation has no new regressions against the baseline | done | `integrated.compare.txt`: regression 0, harness_error 0, corpus_drift 0. `candidate_compare`: 0 new crashes and 0 new silent failures. 3.10–3.13 identical case for case. Upstream token suite 191/39, identical per file. Controls 0 unexpected. Debug identical to Release. |

## Foundation in one line

`bootstrap` at `27ef3c6` is upstream `b428976` plus 3.14 decoding. 3.14
files load and disassemble (219/219 feature cases) and stop explicitly at
decompile. Behavioral passes: 15/15/9 on 3.10/3.11/3.12 and 0 on 3.13/3.14,
unchanged from the baseline.
