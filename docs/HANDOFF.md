# Handoff

Written by Opus (implementation owner) at the end of Part 4.

**Part 4 is READY_FOR_REVIEW, not COMPLETE.** Parts 2 and 3 are also still
READY_FOR_REVIEW. None of them has had an independent review; the user
started Parts 3 and 4 anyway (D-013, D-017).

Before acting, read `AGENTS.md` and `docs/STATUS.md`, and check the
repository itself.

## Repository state

| Item | Value |
| --- | --- |
| Local checkout | `/Users/intzero/Documents/pycdc/pycdc` |
| Fork / branch | https://github.com/mahdi-salmanzade/pycdc, branch `bootstrap` (D-003, D-011) |
| Upstream base | `b4289760970dbc399684f1e155ec6d1ea1cc787e`. Fork `master` equals upstream `master`. |
| Part 4 production commits | `cc7cf1f` jump targets · `e404851` LOAD_CLASSDEREF · `cb77d0b` EXTENDED_ARG · `d8f80f3` float/complex · `315bd39` strings · `cf86619` clear failures |
| Part 4 harness commit | `a1ae263` (decoding checks, suites, gate) |
| Part 4 docs | the commit containing this file (reports and docs) |
| Dirty tree | none intended; `build/` is gitignored |
| Pinned interpreters | `~/.cache/pycdc-harness/python` (3.10.22 / 3.11.17 / 3.12.15 / 3.13.17 / 3.14.9) |

## Completed in Part 4

- **A semantic comparison of pycdas with CPython's own decoding**
  (`harness/tools/decoding_check.py dis`, `harness/workers/dis_dump.py`). It
  checks code-object fields, names, exact constants, every instruction
  (offset, opcode, operand and resolved meaning) and exception tables.
- **Mechanized checks** for hash-based headers, unsupported formats and
  malformed input (seeded truncations and mutations).
- **New suites:** `decoding` (authored) and `decoding-generated` (two-prefix
  `EXTENDED_ARG` operands). Neither is ever executed.
- **Defects found by the comparison and fixed** (one commit each):
  - jump targets ignoring inline caches (3.11+), and 3.11
    `JUMP_IF_*_OR_POP`;
  - `LOAD_CLASSDEREF` name;
  - multiple `EXTENDED_ARG` prefixes;
  - `%g` floats and complex numbers (also wrong in decompiled source);
  - interned Python 3 strings escaped as bytes (`'é'` → `'\xc3\xa9'`, also
    in decompiled source);
  - raw surrogates and bidi or invisible code points;
  - pycdas exiting 0 after a failed load;
  - unknown marshal types misaligning the stream.
- **Gate:** `gate --part 4 --decoding DIR` replaces the four manual items;
  the requirements were only tightened (D-019).
- **Scope** that Part 4 deliberately did not change, and defects left to
  later parts: D-018.

## Reproduce

```bash
cd /Users/intzero/Documents/pycdc/pycdc
git fetch --multiple origin upstream && git switch bootstrap && git pull --ff-only
harness/setup_interpreters.sh                          # once
PYTHON=python3 reports/part4-decoding/reproduce.sh build/part4-repro
# expect: compare regression 0; controls 0 unexpected; upstream 191/39;
#         gate --part 4 PASSED; dis 1953/1953 match;
#         decoding-before/ (pre-Part-4 build) shows the defects
```

It took 9 minutes on the reference host.

## Measured results

Details are in `reports/part4-decoding/README.md`.

**Decoding checks:**

| Check | Current | Pre-Part-4 (control) |
| --- | --- | --- |
| `dis` files matching | 1,953/1,953 | 1,269/1,953 |
| `formats` runs failing clearly | 34/34 | 28/34 |
| `headers` identical | 1,128/1,128 | — |
| `malformed` pycdas crashes or hangs (all versions) | 0 | 0 |
| `malformed` pycdc crashes or hangs on 3.13/3.14 | 0 | 0 |
| `malformed` pycdc crashes or hangs on 3.10–3.12 | 51, all also in the control | 52 |

**Regression checks:**
- `compare`: regression 0.
- Outcomes are identical to the Part 3 foundation.
- Debug = Release.
- Upstream token suite 191/39.

**Decompiled source:** constant rendering changed in 48 feature cases, for
example `1` → `1.0` and `'\xc3\xa9'` → `'é'`. No outcome changed.

## Review requested (do not mark Part 4 COMPLETE without it)

Reviews must contain concrete counterexamples or test evidence, not
agreement.

**Kimi K3 (adversarial tests): the six production commits.**

1. **Jump targets (`cc7cf1f`).**
   - `bc_skip_caches` skips `CACHE` units by reading the code. Construct an
     authored case where an instruction is followed by a `CACHE` unit that
     is not its own cache, or argue none can exist in on-disk bytecode.
   - Check 3.11 `JUMP_IF_*_OR_POP` and `POP_JUMP_BACKWARD_IF_*`.
2. **`EXTENDED_ARG` (`cb77d0b`).** Three prefixes (operands ≥ 2^24) are not
   compiler-reachable in the corpus. Build an authored synthetic code
   object with `code.replace(co_code=...)` under the pinned interpreter
   (never executed) and check pycdas against `dis`.
3. **Floats and complex numbers (`d8f80f3`).**
   - Find a double whose shortest `%.*g` text does not round-trip, or a
     complex value whose rendering does not rebuild both parts exactly.
   - Note: rendering depends on the C locale; pycdc never calls
     `setlocale`.
4. **Strings (`315bd39`).**
   - Check Python 2 interned strings (still bytes), f-string literal parts,
     and the `needs_escape` set.
   - Find invisible or bidi code points that are still written raw.
5. **Clear failures (`cf86619`).** Look for any remaining way pycdas or
   pycdc exits 0 after a failed load.
6. **The comparison tool itself.**
   - Find a semantic difference between pycdas and `dis` that
     `decoding_check.py dis` would not report: parser leniency, constant
     normalization, or EXTENDED_ARG offset normalization.
   - Add a decoding fixture for it.
7. **Reproduce** `reports/part4-decoding/reproduce.sh`.

**ASTRA (coordinator / architecture):**

1. **D-018 (scope).** AST-builder jump arithmetic and stack effects are
   deferred to Part 6, and the `exit(1)` on end of stream is kept. Agree or
   reject.
2. **D-019.** Confirm that pycdc's malformed-input requirement covers
   3.13/3.14 only, with 3.10–3.12 required not to get worse. The current
   3.10/3.11 crashes are pre-existing AST-builder crashes.
3. **Still open from Parts 2 and 3:**
   - D-006 to D-012 and the required-scope policy;
   - D-015 (the Part 3 foundation);
   - D-016 (silent-failure gate condition);
   - artifact sizes.

**Still owed from earlier parts:**
- the Kimi K3 review of the Part 3 commits `200a4cd`/`27ef3c6`;
- the Part 2 reproduction and fixture review.

## Unresolved questions

1. **D-016:** silent-failure accounting in the gates.
2. **CLI contract (Part 8).**
   - pycdc still exits 0 on incomplete output.
   - Load failures now exit 1 in both tools; that is consistent with
     upstream pycdc.
3. **Linux/CI isolation** is unimplemented.
4. **Upstream contribution.** The Part 4 fixes are small, self-contained
   and upstream-shaped (jump display, `EXTENDED_ARG`, constants, strings,
   failures). Opening upstream PRs needs the user's approval (Part 8).

## Next authorized action

None. Wait for the reviews above and for the user to say "continue". Part 5
(expressions, calls, functions and classes) must not start before that.
