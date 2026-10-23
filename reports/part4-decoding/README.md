# Part 4: decoding checked against CPython

Measured 2026-10-23 on `bootstrap` at `a1ae263`: decompiler source `cf86619`
plus the harness. The decompiler sources and the harness were clean. The
interpreters were the pinned CPython 3.10.22 / 3.11.17 / 3.12.15 / 3.13.17 /
3.14.9 on macOS arm64.

Reproduce everything, including the controls:

```bash
PYTHON=python3 reports/part4-decoding/reproduce.sh build/part4-repro
```

This took 9 minutes on the reference host. The files here come from that
script's run into `build/part4/official`.

## What was checked

`harness/tools/decoding_check.py` compares pycdas with the interpreter that
wrote each `.pyc`. Every run happens in the harness sandbox, and no `.pyc` is
executed. The details are in `harness/README.md` ("Decoding checks") and
`harness/requirements.json` (`parts.4.decoding`).

**Corpus:**
- `features`: 73 fixtures.
- `upstream-inputs`: 90 sources.
- **`decoding`** (new): 6 authored inputs:
  - every constant type, including non-ASCII, astral, surrogate and
    invisible text, signed zeros, nan, inf, complex and 3.14 slices;
  - nested code objects, cells and free variables;
  - every jump family;
  - exception tables and `except*`;
  - type parameters and template strings.
- **`decoding-generated`** (new): more than 65,536 names and constants, and
  forward and backward jumps over more than 65,536 code units. These need
  two `EXTENDED_ARG` prefixes. Also 300 locals and arguments.

All suites cover 3.10–3.14 at `-O0/-O1/-O2`. The new suites are compiled,
disassembled and decompiled, never executed.

## Defects found and fixed

Each was found by `decoding_check.py dis` or `formats`. The "before" column
is the same check run on the pre-Part-4 build (`4d29eee`), in
`decoding-before/`.

| Commit | Defect | Before (files affected / occurrences) | After |
| --- | --- | --- | --- |
| `cc7cf1f` | Relative jumps counted from the instruction instead of the end of its inline caches (3.11+); 3.11 `JUMP_IF_*_OR_POP` printed as absolute | jump targets: 3.11 12/102, 3.12 120/549, 3.13 192/2,358, 3.14 213/2,472 | 0 |
| `e404851` | `LOAD_CLASSDEREF` printed without its variable name (3.10/3.11) | 9 files / 12 per version | 0 |
| `cb77d0b` | Only one `EXTENDED_ARG` prefix folded; a second one desynchronized decoding | 3 files / about 236,800 wrong opcodes per version | 0 |
| `c61e67c` | Floats printed with `%g` (`2.0` → `2`, `-0.0` → `0`, `1.4142135623730951` → `1.41421`); complex the same | — | exact, bit for bit |
| `315bd39` | Python 3 interned strings escaped as bytes (`'é'` → `'\xc3\xa9'`, a different string); surrogates written raw (invalid UTF-8); invisible and bidi characters written raw | constants and names: 24–27 files per version | 0 |
| `cf86619` | pycdas exited 0 with a `(Python -1.-1)` / `<NULL>` listing after a failed load; an unknown marshal type code left the stream misaligned | `formats`: 6 of 34 runs unclear | 34/34 clear |

The constant and string defects were in `print_const`/`PycString::print`,
which the decompiler also uses. In this corpus the decompiled source of 48
feature cases changed with them, for example `v('b', 1)` → `v('b', 1.0)` and
`ascii('\xc3\xa9')` → `ascii('é')`. No case's outcome changed against the
Part 3 foundation: the old outputs either failed for other reasons, or the
fixture could not observe the difference (`1 == 1.0`).

## Results after Part 4

| Check | Result |
| --- | --- |
| `dis` (`decoding/DIS.md`) | **1,953/1,953 files match** (all suites, all versions). The old build: 684 mismatched. |
| `headers` | **1,128/1,128 identical** for checked-hash and unchecked-hash variants (byte-identical to `py_compile`'s) |
| `formats` | **34/34 runs fail clearly**: 17 inputs × pycdas, pycdc |
| `malformed` (`decoding/malformed.txt`) | 1,098 source files, **62,586 derived inputs per tool**. pycdas: **0 crashes, 0 hangs** on every version. pycdc on 3.13/3.14: **0 crashes, 0 hangs**. |
| pycdc on malformed 3.10–3.12 (reported, D-019) | 48 crashes (3.10: 29, 3.11: 19), 3 timeouts (3.11: 2, 3.12: 1). All 51 also fail in the pre-Part-4 build on the identical seeded inputs, which had 52. None is new. |
| `compare` against the Part 2 baseline | regression 0, missing coverage 0, harness error 0, corpus drift 0. 120 added cases (the new suites). |
| Behavior and syntax outcomes against the Part 3 foundation | identical case for case |
| Debug build | identical to Release (`compare-debug.txt`) |
| controls | 1,461 cases, 0 unexpected |
| upstream token suite (sandboxed) | PASS=191 FAIL=0 XFAIL=39 XPASS=0, identical per file to Part 1 |
| `gate --part 4` | **PASSED** (`gate-part4.txt`): 429/429 cases at disassemble; `dis` and `headers` 1,128/1,128; `formats` 34 clear; `malformed` 1,098/1,098 |
| `gate --part 5..7` | not passed: 0/162, 0/114, 0/153 (unchanged) |

**The checks catch the defects (controls).** Run against the pre-Part-4 build
on the same files (`decoding-before/`):
- `dis` reports 684 mismatching files: the jump targets, the second
  `EXTENDED_ARG`, constants, strings, names and `LOAD_CLASSDEREF`.
- `formats` reports 6 unclear runs.
- `malformed` finds pycdc's crashes on 3.10/3.11. Every one of them is a
  known AST-builder crash (the `with` family), which shows the campaign
  detects crashes.

## Limitations

- **Not compared:**
  - line-number tables (outside the observation contract, D-008);
  - the per-local kind flags (`co_localspluskinds`), which Python does not
    expose directly and pycdas prints only with `--pycode-extra`;
  - `co_firstlineno`.
- **Decompiler jump arithmetic** in `ASTree.cpp` is not cache-aware and is
  unchanged (D-018, Part 6).
- **Stack effects** are not in this part (D-018, Part 6).
- **The malformed campaign** is seeded and deterministic but small: 40
  derived inputs per file. It is not coverage-guided fuzzing; that, with
  sanitizers, is Part 8.
- **Exit status 0 on malformed input** happens when a mutation leaves a
  decodable file, about 12% of inputs. The requirement is only "no crash,
  no hang".
- **Decompiler defects found here and left to later parts** (D-018):
  - `ASTree.cpp:1957` reads past the end of the bytecode;
  - `seq[(1:2, 3)]` printing;
  - 3.14 constant slices printed as `slice(...)` calls;
  - AST-builder crashes on malformed 3.10/3.11 input.

## Files

| File | Content |
| --- | --- |
| `decoding/` | the four reports gate reads (`dis`, `headers`, `formats`, `malformed`; JSON gzip-compressed), `DIS.md`, `malformed.txt` |
| `decoding-before/` | the same `dis`, `formats` and `malformed` checks on the pre-Part-4 build: the controls |
| `results/` | the corpus run (Release and Debug), controls, upstream per-file outcomes |
| `SUMMARY.md`, `CONTROLS.md` | run summary and controls |
| `compare.txt`, `compare-debug.txt`, `gate-part{4,5,6,7}.txt` | baseline comparison, Release vs Debug, gate output |
| `reproduce.sh` | the full reproduction |

To re-run `gate` on these files, gunzip `results/*.json.gz` and
`decoding/*.json.gz` first. `gate` reads plain JSON, and the
`decoding/<check>.json` names must be kept.
