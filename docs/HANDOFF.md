# Handoff

Written by Opus (implementation owner) at the end of Part 3.

**Part 3 is READY_FOR_REVIEW, not COMPLETE.** Part 2 is also still
READY_FOR_REVIEW; its reviews were never done, and the user started Part 3
anyway (D-013).

Before acting, read `AGENTS.md` and `docs/STATUS.md`, and check the
repository itself.

## Repository state

| Item | Value |
| --- | --- |
| Local checkout | `/Users/intzero/Documents/pycdc/pycdc` |
| Fork / branch | https://github.com/mahdi-salmanzade/pycdc, branch `bootstrap` (D-003, D-011) |
| Upstream base | `b4289760970dbc399684f1e155ec6d1ea1cc787e`. Fork `master` equals upstream `master`. |
| Part 3 commits | see the list below |
| Production code changed in Part 3 | `200a4cd` and `27ef3c6` only (3.14 decoding) |
| Dirty tree | none intended; `build/` is gitignored |
| Candidate refs | `refs/remotes/upstream/pr/616` = `e3936f8`, `upstream/pr/617` = `88e988b`, `upstream/pr/596` = `0b47e4f` (remote-tracking refs, not branches) |
| Pinned interpreters | `~/.cache/pycdc-harness/python` (3.10.22 / 3.11.17 / 3.12.15 / 3.13.17 / 3.14.9) |

**Part 3 commits:**
- `d0452df`: harness evaluation tools.
- `200a4cd`: 3.14 slice constants.
- `27ef3c6`: 3.14 magic number and opcode table.
- `332b5b7`: harness `NAME=DIR` suites.
- `abe7150`: harness `compare` noise normalization and the stricter `gate`.
- The commit containing this file: reports and docs.

## Completed in Part 3

- **Inventory and isolation:**
  - Upstream history and the related issues and PRs are inventoried
    (`reports/part3-candidates/README.md`).
  - PRs #616 and #617 are pinned to their heads and built in isolated
    detached clones (D-014).
- **Measurement:** each build was run against the frozen corpus, upstream's
  token suite (sandboxed) and both PRs' own inputs (L1, never executed). An
  unmodified base clone served as the control.
- **Tools:**
  - `harness/tools/candidate_compare.py` counts silent failures, which
    `compare` does not.
  - `harness/tools/upstream_suite.py` runs the token suite sandboxed.
  - `opcode_coverage.py --source-root`.
  - `NAME=DIR` compile-only suites.
- **Harness corrections:**
  - `compare` ignores run-varying cause text: crash signal, timeout
    duration, internal opcode numbers.
  - `gate` no longer prints PASSED while manual-evidence requirements are
    outstanding. Part 4 previously showed "GATE PASSED" next to four
    unmet manual items.
- **Integration (D-015):** only the 3.14 decoding layer was adopted, with
  attribution to #596, #616 and #617. Both PRs' AST changes were rejected
  for now, with reasons recorded. They are kept as references for Parts 5–7.

## Reproduce

```bash
cd /Users/intzero/Documents/pycdc/pycdc
git fetch --multiple origin upstream && git switch bootstrap && git pull --ff-only
harness/setup_interpreters.sh                        # once
PYTHON=python3 reports/part3-candidates/reproduce.sh build/part3-repro
# expect:
# - every build's token suite: PASS=191 FAIL=0 XFAIL=39 XPASS=0
# - integrated compare: regression 0, harness_error 0, corpus_drift 0
# - comparison.json counts equal to reports/part3-candidates/comparison.json
```

It took 5.5 minutes on the reference host (macOS arm64, 8 jobs). It
rebuilds three candidates and does four full corpus runs, the controls and
the contributor-input runs.

**My own reproduction (exit 0):**
- base, #617 and the integrated build reproduce case for case;
- one pre-existing upstream crash changed signal (SIGSEGV to SIGBUS);
- #616's `loops/nested_exits` crash varies between runs (SIGSEGV, SIGBUS,
  or an uncaught `std::vector` exception).

Details are in `reports/part3-candidates/README.md`, "Reproduction check".

## Measured results

Details are in `reports/part3-candidates/`.

**Feature fixtures, behavioral PASS / applicable:**

| Build | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
| --- | --- | --- | --- | --- | --- |
| baseline | 15/192 | 15/201 | 9/207 | 0/210 | 0/219 |
| PR #616 | 15/192 | 21/201 | 17/207 | 26/210 | 29/219 |
| PR #617 | 15/192 | 15/201 | 12/207 | 21/210 | 18/219 |
| integrated | 15/192 | 15/201 | 9/207 | 0/210 | 0/219 |

**New silent mismatches against the baseline:**
- **#616:** 162. Of these, 61 are on 3.10–3.12. It also adds 9 pycdc
  crashes (SIGSEGV on `loops/nested_exits`) and 12 hangs in recovered
  programs.
- **#617:** 60. Of these, 24 are on 3.10–3.12. It also adds 6 crashes
  (SIGSEGV on `branches/short_circuit`).
- **Integrated:** 0 new silent failures and 0 new crashes.

**Other findings:**
- Unmarked output is correct for only 18–42% of cases, in every build
  including upstream.
- Each PR passes its own inputs (#616: 54/60 on 3.13; #617: 30/30) but
  does much worse on the other's.

**Counterexamples on authored probes** (`reports/part3-candidates/probes/`,
compiled and decompiled only):
- **#616:**
  - `x ^= y` becomes `x = x[y]` on 3.11/3.12;
  - a generator's `yield`s are dropped;
  - `except E: x = 1` becomes `except E as x:`.
- **#617:** a decorator expression is evaluated after the function's default
  values.
- **Upstream:** silently mis-decompiles the decorator and except-return
  probes on 3.11/3.12.
- **Corpus gap:** #616's `^=` regression on 3.11/3.12 was not caught by the
  behavioral corpus. The proposed fixture additions are in `REVIEW_NOTES.md`.

**Integrated build:**
- 3.14: 219/219 feature cases load and disassemble.
- All decompile failures are explicit: `MAKE_FUNCTION` 168, `LOAD_SMALL_INT`
  48, `MAKE_CELL` 3.
- 3.10–3.13 are unchanged case for case.

## Review requested (do not mark Part 3 COMPLETE without it)

Reviews must contain concrete counterexamples or test evidence, not
agreement.

**Kimi K3 (adversarial tests): review the production commits `200a4cd` and
`27ef3c6`.**

1. **Slice loader** (`PycSlice::load`).
   - Check back-reference indexing against CPython 3.14 `marshal.c`.
   - Construct a 3.14 `.pyc` where a slice constant is referenced twice, or
     contains a referenced object, and confirm pycdas lists it correctly.
     Build it from authored source with the pinned 3.14.9, not from
     untrusted files.
2. **Opcode table.** Re-derive `bytes/python_3_14.cpp` from
   `dis.opmap`/`opcode` of 3.14.9 yourself; do not rely on
   `opcode_coverage.py` alone.
   - Check that no ≤3.13 table or AST path changed. The case-for-case
     identical results are evidence, but they are not proof.
3. **pycdas operands.** Check the new operand rendering (`END_ASYNC_FOR`
   target, `LOAD_SPECIAL`, `LOAD_COMMON_CONSTANT`, `LOAD_FAST_BORROW*`,
   `BINARY_OP 26`) against `dis` on authored code. Report any mismatch.
4. **Silent misreads.** Find a 3.14 construct where the unchanged AST
   builder now silently misinterprets 3.14 bytecode instead of stopping. The
   corpus found none, but it is small.
5. **Reproduce** `reports/part3-candidates/reproduce.sh` and report any
   count that differs.
6. **Review the harness changes:**
   - `compare` normalization (`CAUSE_NOISE`): could it hide a real change?
   - the stricter `gate`;
   - `NAME=DIR` suites.
7. **Review the proposed fixture additions** in `REVIEW_NOTES.md`.
8. **Part 2 review items** from the previous handoff are still open. See
   git history of this file at `a984a29`.

**ASTRA (coordinator / architecture):**

1. **Rule on D-015.** Is adopting only the decoding layer the right
   foundation? Is deferring all AST work from #616/#617 to Parts 5–7
   justified?
2. **Rule on D-016**, the proposed gate tightening for silent failures in
   3.10–3.12 and `upstream-inputs`, including its trade-off for fixes to
   shared opcodes.
3. **Part 2 items** (D-006 to D-012, the required-scope policy, artifact
   sizes) are still open. Part 3 stores raw results gzip-compressed (about
   120 KB each).

## Unresolved questions

1. **D-016:** silent-failure accounting in the gates (see above).
2. **CLI contract (Part 8, from Part 2).**
   - pycdc exits 0 on incomplete output. #617's AST changes would make
     some unsupported shapes exit nonzero via exceptions, which was not
     adopted.
   - The 18–42% correctness of unmarked output strengthens the case for
     an explicit failure contract.
3. **Linux/CI isolation** is unimplemented (from Part 2).
4. **Upstream contribution.** The adopted 3.14 decoding commits are small and
   upstream-shaped. Opening an upstream PR needs the user's approval
   (Part 8). Several open upstream PRs (#566, #596, #605, #616, #617) overlap
   with each other.

## Next authorized action

None. Wait for the reviews above and for the user to say "continue". Part 4
(make bytecode decoding trustworthy) must not start before that.
