# Differential test harness

This harness measures whether pycdc reconstructs Python source that **behaves
like the compiled program**. It does not check whether the output looks like
the original source. It is test tooling and is not part of the pycdc binaries.

## Quick start

```bash
# once: pinned interpreters (needs network for the download only)
harness/setup_interpreters.sh
python3 harness/difftest.py interpreters            # verifies exact versions + magic

# build the decompiler under test
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release && cmake --build build/release -j8

# validate the harness itself (must report 0 unexpected control outcomes)
python3 harness/difftest.py controls --out build/controls.json --summary build/controls.md

# measure pycdc
python3 harness/difftest.py run --suite features,upstream-inputs \
    --out build/results.json --summary build/results.md

# compare with the frozen baseline (exit 1 on regressions, missing coverage or harness errors)
python3 harness/difftest.py compare reports/part2-baseline/baseline.json build/results.json
```

The host interpreter only orchestrates. Use any CPython 3.10 or newer; only
the standard library is needed. The fixtures are compiled and executed by the
pinned **target** interpreters in `harness/interpreters.json`:

| Target | Pinned build | `.pyc` magic |
| --- | --- | --- |
| 3.10 | 3.10.22 | 3439 |
| 3.11 | 3.11.17 | 3495 |
| 3.12 | 3.12.15 | 3531 |
| 3.13 | 3.13.17 | 3571 |
| 3.14 | 3.14.9 | 3627 |

They are uv-managed python-build-standalone builds, installed under
`~/.cache/pycdc-harness/python` with `--no-bin`, so the user's own `python3.x`
links are untouched. A missing interpreter is reported as `MISSING` coverage.
A wrong version or magic is also reported as `MISSING`, never as success.

To evaluate a build from another tree (Part 3 candidates), pass
`--pycdc <tree>/build/pycdc --source-root <tree>`. The load probe is then
compiled against that tree's headers and `libpycxx.a`.

## Suites

| Suite | Sources | Validated up to | Executed? |
| --- | --- | --- | --- |
| `features` | `harness/fixtures/<category>/*.py`: authored, deterministic fixtures with an `observe()` driver | behavior | yes, in the sandbox |
| `upstream-inputs` | upstream `tests/input/*.py` | syntax | **never**; compiled and decompiled only |
| `decoding` | `harness/decoding/*.py`: Part 4 decoding inputs (every constant type, nested code objects, every jump family, exception tables) | syntax | **never**; compiled, disassembled and decompiled only |
| `decoding-generated` | `build/decoding-generated/*.py`, written by `harness/tools/decoding_check.py generate --out build/decoding-generated`: operands that need two `EXTENDED_ARG` prefixes | syntax | **never**; compiled, disassembled and decompiled only |
| `NAME=DIR` | any directory of `*.py`, such as a pull request's own test inputs (`--suite contrib=path/to/dir`) | syntax | **never**; compiled and decompiled only |

A fixture header may declare `# requires: >=3.12` (comma-separated clauses).
Cases outside that range are reported as `N/A`, which is distinct from
`FAIL` and from `MISSING`. For `upstream-inputs`, a source that the target
interpreter cannot compile (Python 2 syntax, for example) is `N/A`.

## Stages and outcomes

Each case is one (fixture, interpreter, optimization level) triple, with
`-O0`, `-O1` and `-O2` all used by default. The fixture is compiled by the
target interpreter into a timestamp-based `.pyc`. The source mtime is pinned,
so the bytes are deterministic and their SHA-256 is recorded. Then:

| Stage | Passes when | Failure kinds |
| --- | --- | --- |
| load | `harness/tools/load_probe.cpp` (only `PycModule::loadFromFile` from the build's own `libpycxx.a`) loads the file as the right version, silently | error, crash, timeout |
| disassemble | `pycdas` exits 0, writes nothing to stderr, and prints no `<INVALID>` / `<N>` opcodes | error, invalid_opcode, diagnostic, crash, timeout |
| decompile | `pycdc` exits 0, writes nothing to stderr, and emits no `# WARNING: Decompyle incomplete` | error, incomplete, diagnostic, crash, timeout |
| syntax | the recovered source compiles under the same interpreter at the same `-O` level | syntax_error, crash, timeout |
| behavior | the recovered source's observation equals the compiled `.pyc`'s observation | mismatch, error, crash, timeout |

A case is classified **once, at its earliest failing stage**. Later stages
still run whenever there is usable output. pycdc output that is marked
incomplete or has diagnostics is still syntax-checked and executed for
information, but it can never count as PASS. Outcomes:

- `PASS`: every stage passed (`validated_to` says whether that was up to behavior or only up to syntax).
- `FAIL`: has a `stage`, a `kind` and a normalized `cause`. `crash`, `timeout` and `incomplete` are kinds and are counted separately in the summaries.
- `N/A`: the fixture does not apply to this version.
- `MISSING`: the pinned interpreter is unavailable.
- `HARNESS_ERROR`: the fixture itself failed to compile, or the reference run failed. This always needs fixing and is never a pycdc result.

`compare` reports each case relative to a frozen baseline as one of:
`regression` (PASS became non-PASS, or a failure moved to an earlier stage),
`fixed` (XPASS-like), `still_failing` (XFAIL-like), `failure_changed`,
`unchanged_pass`, `not_applicable`, `missing_coverage`, `harness_error`,
`added`, `removed` or `corpus_drift` (a compiled `.pyc` hash changed).

`still_failing` versus `failure_changed` compares the stage, the kind and
the cause. Some parts of a cause vary without the failure changing, and
these are ignored:
- pycdc's internal opcode number in "Unsupported opcode: NAME (N)", which
  shifts when opcodes are added;
- SIGSEGV versus SIGBUS for a crash, which depends on the faulting address;
- the wall-clock duration in a timeout.

A failure that becomes silently wrong output (from an incomplete marker to
a behavior mismatch) is `failure_changed`, not `regression`. Use
`tools/candidate_compare.py` to count those (D-016).

`gate --part N` passes only if every requirement for Parts 4..N is checked
and met. From Part 4 on it also needs `--decoding DIR`: the four reports of
`tools/decoding_check.py` for the same binaries (see "Decoding checks"). A requirement listed as `not_yet_mechanized` in
`requirements.json` counts as a problem until a tool checks it.

## Observation contract

`harness/workers/observe.py` runs the code object, either marshal-loaded from
the `.pyc` (the reference) or compiled from candidate source at the same
optimization level, in a fresh module named `fixture`. It then calls
`observe()`. Both runs use the same interpreter, flags, `PYTHONHASHSEED=0`, and
a fresh process. The harness compares these channels:

| Channel | Content |
| --- | --- |
| `module.transcript` / `module.outcome` | ordered stdout+stderr text while the module body runs; return or raised exception |
| `globals.outcome` | structural description of every non-dunder module global after execution: values; functions as qualname plus parameter list with defaults; classes with bases, metaclass and every class-dict entry, including dunder methods |
| `observe.transcript` / `observe.outcome` | the same, for `observe()`; its return value is described structurally |
| `finalize.transcript` | output of an explicit `gc.collect()`; automatic GC is disabled while the fixture runs, so cyclic garbage is finalized deterministically here |
| `process.stdout` / `process.stderr` | anything printed at interpreter exit (atexit handlers, late finalizers) |
| `env` | interpreter version, `sys.flags.optimize`, a `hash()` probe; must agree, otherwise `HARNESS_ERROR` |

Exceptions are described by qualified type, `str()`, `args`, `__cause__`,
`__context__`, `__suppress_context__`, `__notes__`, and `ExceptionGroup`
members, recursively. Sets are compared order-independently. Dicts and all
other values are compared in order. Warnings are formatted without file or
line, and the filter is `always`, so de-duplication cannot depend on line
numbers.

**Deliberate exclusions.** These are not observed, so differences in them are
not failures:

- source text, comments, formatting, and `inspect.getsource`;
- tracebacks, line and column numbers, `co_positions`, `__firstlineno__`, and
  warning locations (`line N` is also normalized in process stderr);
- code-object attributes (`__code__`, `co_*`), bytecode, and constant-table
  layout;
- object identity and addresses (` at 0x…` in default reprs is normalized);
- compile-time warnings of the candidate source, such as `SyntaxWarning`. The
  syntax stage records them, but they are not behavior;
- annotations are not evaluated by the harness itself, because 3.14 defers
  them. Fixtures that care observe them explicitly;
- timing, memory use, recursion-depth limits and garbage-collection timing,
  apart from the explicit `finalize` step.

Passing shows equal observations for these fixtures, inputs and drivers. It
is evidence of equivalence, not proof that the outputs are equivalent for
every input.

## Controls (validating the harness)

`difftest.py controls` must report **0 unexpected outcomes** before results
are trusted. It runs two kinds of control:

- **Positive controls:** every fixture's own source is used as the candidate
  and must match its compiled `.pyc` at every version and `-O` level. This
  catches non-deterministic fixtures and harness asymmetries.
- **Negative controls** (`harness/controls/controls.json`): each one is an
  exact, single-occurrence text replacement that changes behavior. Examples
  are a swapped evaluation order, an extra `__bool__` call, a dropped
  `__cause__`, a changed default, a dropped statement, a changed atexit
  output, and output moved from stderr to stdout. Each must be detected on its
  declared channel. `detect_at` lists the `-O` levels where the mutated code
  exists in the compiled program; for example, `assert` is absent at `-O`, so
  the change cannot be observed there.

## Isolation and safety

Every process the harness starts runs through `harness/sandbox.py`:

- The environment is scrubbed, so no credentials are passed through.
- `HOME` and `TMPDIR` point to the case directory.
- On macOS a `sandbox-exec` profile denies all network access, denies writes
  outside the case directory, and denies reads under `$HOME` except the
  interpreters and the repository.
- Resource limits cap CPU time, file size (stdout and stderr are files) and
  core dumps.
- Wall-clock timeouts kill the whole process group.
- macOS does not enforce `RLIMIT_AS`, so memory is bounded only by the CPU
  limit and the timeout.
- Other platforms have no sandbox profile yet. Running there requires
  `--sandbox none --allow-unisolated`, which is recorded in the results. Linux
  isolation is planned with CI (Part 8).

Policy:

- Only reviewed fixtures in `harness/fixtures/` are executed.
- `upstream-inputs` and `NAME=DIR` sources are compiled and decompiled, never
  run.
- A binary built from unreviewed source (a pull request under evaluation)
  runs only in this sandbox, including for upstream's token suite
  (`tools/upstream_suite.py`).
- The decompiler itself is run on fixture `.pyc` files only.
- Unknown `.pyc` files from issues or the internet must not be added as
  fixtures. Parsing them would also need this sandbox.

## Decoding checks (Part 4)

`harness/tools/decoding_check.py` checks pycdas against the interpreter that
wrote each `.pyc`. Every pycdas run and every reference run happens in the
sandbox, and no `.pyc` is executed. It runs on the `.pyc` files of a
`difftest.py run` work root:

```bash
python3 harness/tools/decoding_check.py generate --out build/decoding-generated
python3 harness/difftest.py run --suite features,upstream-inputs,decoding,decoding-generated \
    --workroot build/difftest --out build/results.json
T=harness/tools/decoding_check.py; D=build/decoding
python3 $T dis --workroot build/difftest --suites features,upstream-inputs,decoding,decoding-generated \
    --workdir $D --out $D/dis.json --summary $D/DIS.md
python3 $T headers --workroot build/difftest --suites features,decoding,decoding-generated \
    --workdir $D --out $D/headers.json
python3 $T formats --workroot build/difftest --workdir $D --out $D/formats.json
python3 $T malformed --workroot build/difftest --suites features,decoding --workdir $D \
    --out $D/malformed.json
python3 harness/difftest.py gate --part 4 --results build/results.json --decoding $D ...
```

| Check | What must hold |
| --- | --- |
| `dis` | pycdas equals `marshal`/`dis` of the same interpreter (`workers/dis_dump.py`) at the semantic level: code-object fields; names; local, cell and free names; exact constant values; every instruction (offset with `EXTENDED_ARG` folded, opcode, raw operand, and the resolved jump target, name, constant, local or comparison); exception-table entries. Formatting is not compared. |
| `headers` | the checked-hash and unchecked-hash forms of every `.pyc` (`workers/pyc_variants.py`, byte-identical to `py_compile`'s) give the same pycdas and pycdc results as the timestamp form |
| `formats` | 17 crafted undecodable inputs make both tools exit nonzero with a message and no listing |
| `malformed` | seeded truncations and byte mutations of every `.pyc` never crash, hang or hit the output limit in pycdas (any version) or pycdc (3.13, 3.14) |

The reference side folds `EXTENDED_ARG` prefixes into the instruction they
extend, at the offset of the first prefix, and omits `CACHE` units, as
pycdas prints them. It resolves constant operands from `co_consts`
directly, because `dis` on 3.11 leaves some of them, such as `KW_NAMES`,
unresolved.

## Other tools

- `harness/tools/opcode_coverage.py --pyc-root build/difftest/features --out
  report.md [--source-root TREE]` cross-checks `bytes/python_X_Y.cpp` and the
  `ASTree.cpp` cases against each pinned interpreter's `dis.opmap`, and
  against the opcodes the corpus uses.
- `harness/tools/candidate_compare.py --baseline BASE.json NAME=RESULTS.json
  ...` compares candidate builds with a baseline. It reports, per suite and
  version:
  - stage outcomes, tool crashes, silent mismatches (including recovered
    programs that hang) and silent invalid output;
  - fixed and regressed cases, and failures that moved to an earlier stage;
  - new and resolved crashes and silent failures;
  - overlap between candidates.

  Unlike `difftest.py compare`, it separates a case that went from "marked
  incomplete" to "silently wrong".
- `harness/tools/upstream_suite.py --build-dir DIR --json OUT.json` runs
  upstream's token-level suite against `DIR/pycdc` inside the sandbox.
- `reports/part1-baseline/per_file_outcomes.py` reports upstream's own
  token-level suite per file.
