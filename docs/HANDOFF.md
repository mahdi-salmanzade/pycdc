# Handoff

Written by Opus (implementation owner) at the end of Part 2. **Part 2 is
READY_FOR_REVIEW, not COMPLETE.** Before acting, read `AGENTS.md` and
`docs/STATUS.md`, and check the repository itself.

## Repository state

| Item | Value |
| --- | --- |
| Local checkout | `/Users/intzero/Documents/pycdc/pycdc` |
| Fork / branch | https://github.com/mahdi-salmanzade/pycdc, branch `bootstrap` (D-003, D-011) |
| Upstream base | `b4289760970dbc399684f1e155ec6d1ea1cc787e`. Fork `master` equals upstream `master`. |
| Part 2 commits | `8d37b75` harness, fixtures, requirements, audit · `d1f8e40` corpus opcode gaps closed · `afc5000` path scrubbing, failure manifest, `reproduce.sh` (the **baseline was frozen at this clean commit**) · the commit containing this file adds `reports/part2-baseline/` and the docs |
| Decompiler source | unchanged from upstream `b428976` (verified with `git diff --stat`) |
| Dirty tree | none intended; `build/` is gitignored |
| Pinned interpreters | `~/.cache/pycdc-harness/python` (3.10.22 / 3.11.17 / 3.12.15 / 3.13.17 / 3.14.9). Install with `harness/setup_interpreters.sh`. |

## Completed in Part 2

- **Architecture audit** (`docs/ARCHITECTURE.md`): the pipeline from `.pyc`
  to source, with `file:line` references. Claims marked **[verified]** were
  re-read or confirmed by execution.
- **Differential harness** (`harness/`, see `harness/README.md`):
  - pinned interpreters (D-006) and the sandbox (D-007);
  - the observation contract (D-008) and the load probe with earliest-stage
    attribution (D-009);
  - the `run`, `controls`, `compare`, `gate`, `list` and `summarize`
    commands;
  - the opcode-coverage and failure-manifest tools.
- **Feature corpus v1:** 73 authored fixtures in 13 categories. Each is
  assigned to the roadmap part whose constructs it uses (D-010).
- **Required scope and exclusions:** `harness/requirements.json` and
  `docs/FEATURE_MATRIX.md`.
- **Harness validation:** 29 negative controls and positive controls on
  every fixture, version and `-O` level.
- **Frozen baseline:** `reports/part2-baseline/`, with a README holding
  provenance, hashes and commands.

## Reproduce

```bash
cd /Users/intzero/Documents/pycdc/pycdc
git fetch --multiple origin upstream && git switch bootstrap && git pull --ff-only
harness/setup_interpreters.sh                       # once
PYTHON=python3 reports/part2-baseline/reproduce.sh build/part2-repro
# expect: 0 unexpected control outcomes; upstream PASS=191 FAIL=0 XFAIL=39 XPASS=0;
#         compare: regression 0, failure_changed 0, missing_coverage 0,
#         harness_error 0, corpus_drift 0 (corpus_drift is expected off macOS arm64)
python3 harness/difftest.py gate --part 5 --results build/part2-repro/results.json \
    --controls build/part2-repro/controls.json \
    --upstream build/part2-repro/upstream_per_file_outcomes.json --limit 5
# expect: GATE NOT PASSED (baseline: 0/162 Part 5 cases)
```

The whole reproduction takes about 2 minutes on the reference host: 40 s for
the controls and 40 s for each run.

## Measured results (details in `reports/part2-baseline/`)

**Features, behavioral PASS / applicable cases:**

| 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
| --- | --- | --- | --- | --- |
| 15/192 | 15/201 | 9/207 | 0/210 | 0/219 |

**Where cases first fail:**

- 3.14 fails at load in all 219 cases (`Bad MAGIC!`).
- 3.13 is incomplete at decompile in all 210 cases; 204 of them stop at
  `MAKE_FUNCTION`.
- 3.10–3.12 fail mostly at decompile: unhandled `MAKE_CELL`,
  `RETURN_GENERATOR`, `JUMP_IF_NOT_EXC_MATCH`, `CALL_FUNCTION_EX` and others.

**Other measurements:**

- **63 silent semantic mismatches** and 9 crashes (SIGSEGV in `with`,
  3.10/3.11).
- None of the 414 outputs marked incomplete or with diagnostics behaved
  correctly.
- **Upstream inputs (L1, never executed):** 135/114/120/66/0 of 165
  compilable cases per version.
- **Upstream token suite:** unchanged, 191 PASS / 39 XFAIL / 0 XPASS.
- **Gate dry runs** (`GATES.md`):
  - Part 4: 210/429 cases reach disassemble, all of them 3.13.
  - Parts 5, 6, 7: 0/162, 0/114 and 0/153 cases pass.
- **Opcode tables:** correct for 3.10–3.13. The AST builder lacks cases for
  20/28/32/41 opcodes the corpus uses. 3.14 has no table.
- **3.14 marshal (verified):** version 5 stores `slice` constants (type code
  `':'`), which pycdc's `CreateObject` does not handle.

## Review requested (do not mark Part 2 COMPLETE without it)

Reviews must contain concrete counterexamples or test evidence, not
agreement.

**Kimi K3 (investigator / adversarial tests):**

1. Run `reproduce.sh` in your own environment and report the full `compare`
   output, including any `corpus_drift`.
2. **Try to break the harness.**
   - Find a semantic change that the observation contract misses. If you find
     one, add a negative control (`harness/controls/controls.json`) that fails
     today.
   - Find a false positive: an equivalent rewrite that is reported as a
     mismatch.
3. **Review all 73 fixtures** for:
   - determinism;
   - hidden dependence on excluded behavior (line numbers, identity);
   - correct part assignment under D-010;
   - missing constructs per category.

   Propose additions. Fixtures may be added; none may be removed or weakened.
4. **Check `docs/ARCHITECTURE.md`.** Re-check at least the claims *not*
   marked [verified], and the hazard table.

**ASTRA (coordinator / architecture):**

1. **Rule on the required-scope policy** in `harness/requirements.json`:
   - 3.13 and 3.14 must pass, and 3.10–3.12 must not regress;
   - the per-part fixture lists;
   - the "always" conditions;
   - the exclusions.

   After review, the policy may only be tightened.
2. **Review decisions D-006 to D-012.** In particular:
   - the observation-contract exclusions (D-008);
   - macOS-only isolation until Part 8 (D-007);
   - `bootstrap` as the integration branch (D-011).
3. Decide whether keeping `baseline.json` (1.9 MB) and `controls.json`
   (0.4 MB) in Git is acceptable, or whether they should be compressed or
   externalized. The rule is to keep large generated artifacts out of Git
   unless they are deliberate.

## Unresolved questions

1. **CLI contract (Part 8).** pycdc exits 0 even when it emits the incomplete
   marker or diagnostics. pycdas exits 0 after `Bad MAGIC!`. Should partial
   output exit nonzero? A change would affect upstream users and needs a
   decision.
2. **Linux and CI isolation** (`bwrap`/`unshare`/containers) is unimplemented.
   Off macOS the harness refuses to run without `--allow-unisolated`.
3. **Fixture granularity.** The fixtures are broad. Parts 5–7 must add minimal
   regressions before each fix, and those join the required set.
4. **Part 3 inputs.** PRs #616 and #617 have not been inspected yet; that is
   Part 3 and is not authorized.

## Next authorized action

None. Wait for the reviews above and for the user to say "continue". Part 3
(evaluate upstream work, PRs #616/#617) must not start before that.
