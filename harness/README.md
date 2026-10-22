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
- `upstream-inputs` sources are compiled and decompiled, never run.
- The decompiler itself is run on fixture `.pyc` files only.
- Unknown `.pyc` files from issues or the internet must not be added as
  fixtures. Parsing them would also need this sandbox.

## Other tools

- `harness/tools/opcode_coverage.py --pyc-root build/difftest/features --out
  report.md` cross-checks `bytes/python_X_Y.cpp` and the `ASTree.cpp` cases
  against each pinned interpreter's `dis.opmap`, and against the opcodes the
  corpus uses.
- `reports/part1-baseline/per_file_outcomes.py` reports upstream's own
  token-level suite per file.
