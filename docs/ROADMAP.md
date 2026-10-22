# Roadmap

Source of truth for the parts and their acceptance criteria. Work proceeds one
part at a time. A part starts only after the previous gate has passed and the
user has said "continue". Statuses: `NOT_STARTED`, `IN_PROGRESS`, `BLOCKED`,
`READY_FOR_REVIEW`, `COMPLETE`. Current state: `docs/STATUS.md`.

Scope: CPython `.pyc` → readable, behaviorally equivalent source. The initial
focus is 3.13 and 3.14. Keep regression coverage for 3.10, 3.11 and 3.12 and
upstream's older-version tests. Do not silently add newer versions. Out of
scope: exact comments and formatting, Cython/Nuitka binaries, packaging
extraction, deobfuscation, and adaptive/specialized runtime bytecode (unless
separately approved).

| Part | Title | Status |
| --- | --- | --- |
| 1 | Fork and establish the workspace | COMPLETE (2026-10-22) |
| 2 | Audit the implementation and establish the benchmark | see STATUS.md |
| 3 | Evaluate existing upstream work | NOT_STARTED |
| 4 | Make bytecode decoding trustworthy | NOT_STARTED |
| 5 | Recover expressions, calls, functions, and classes | NOT_STARTED |
| 6 | Recover structured control flow and exceptions | NOT_STARTED |
| 7 | Cover modern language features and interactions | NOT_STARTED |
| 8 | Harden, document, and prepare contributions | NOT_STARTED |

## Part 1 — Fork and establish the workspace

Create the fork with `gh`, set up safe remotes, build the unmodified project,
attempt the existing checks, and commit and push the bootstrap documents. No
decompiler logic changes and no outside contributions merged.

**Gate:** fork ownership and parent verified. Remotes correct. Starting commit
recorded. Project builds. Existing checks attempted, with honest results.
Bootstrap documents committed and pushed. Pre-existing test failures may be
recorded as baseline. A broken build or missing required tool is a blocker.

## Part 2 — Audit the implementation and establish the benchmark

Map the pipeline from the real code: `.pyc` load → marshal/code objects →
opcode decode → stack handling → control-flow reconstruction → AST → source
emission. Build a reproducible fixture harness on pinned CPython interpreters.
Compile each fixture with its target interpreter and validate recovered source
with the same interpreter, at `-O0`, `-O1` and `-O2` where applicable. Measure
loading, disassembly, source generation, syntax compilation and behavioral
comparison as separate stages, and attribute each failure to its earliest stage.
The feature matrix covers expressions, calls, functions, closures, classes,
imports, branches, loops, comprehensions, exceptions, generators, async code
and version-specific syntax. Version-inapplicable fixtures are kept distinct
from failures and from missing coverage. The differential-test mechanism
compares return values, stdout/stderr, exception types and messages,
mutations, side-effect order and iteration behavior. Negative controls must
show that it detects deliberate semantic changes. Document the observation
contract and its exclusions (for example source introspection and traceback
line numbers). Freeze a versioned baseline corpus with hashes and exact
commands, classify the failures, and define the required fixtures and
exclusions for later parts. Do not reduce these later to pass a gate.

**Gate:** another model can reproduce the baseline from the recorded commands.
Reports distinguish every stage and outcome. The harness catches deliberate
semantic changes. The required feature scope is explicit.

## Part 3 — Evaluate existing upstream work

Inspect upstream history, relevant issues, and PRs #616 and #617, with their
exact head commits and current status. Treat their claims as hypotheses.
Build upstream and each candidate in isolation, and run the frozen corpus and
upstream suite against each. Compare gains, regressions, crashes, silent
semantic mismatches, code quality and overlap. Adopt changes selectively, with
attribution and independent review. Record rejected approaches, then re-run
the full baseline after integration.

**Gate:** a reproducible comparison report exists. The integration decision is
justified. Independent review is recorded. No new regressions against the
baseline.

## Part 4 — Make bytecode decoding trustworthy

Headers, magic values, marshal and code-object layouts, opcode tables,
arguments, `EXTENDED_ARG`, inline-cache accounting, offsets, jump targets,
exception tables and stack effects. Use released CPython source and matching
tools as references, and keep CPython opcode values distinct from pycdc's
internal enum. Compare pycdas output with normalized `dis` output at the
semantic level, including nested code objects, names and constants, operands,
targets and exception ranges. Keep version-specific rules explicit.

**Gate:** required decoding fixtures match the reference. Unsupported formats
fail clearly. Malformed inputs fail safely. Covered versions do not regress.
Required scope: `harness/requirements.json` part 4 (`difftest.py gate --part 4`
plus the listed manual evidence).

## Part 5 — Expressions, calls, functions, classes

Literals and containers, operators, indexing, attributes, imports,
assignment and unpacking, calls (positional, keyword, `*`/`**`), defaults,
closures, decorators, function creation and basic classes. Evaluation order,
stack balance, closure binding, aliasing and mutation are correctness
requirements. Each fix starts with a minimal failing regression, plus
interaction and side-effect-sensitive cases.

**Gate:** required fixtures pass syntax and behavioral checks on their
applicable versions. Independent review is complete. No new regressions.
Required scope: `harness/requirements.json` part 5 (`difftest.py gate --part 5`).

## Part 6 — Structured control flow and exceptions

`if`/`elif`/`else`, short-circuit and conditional expressions, `for`/`while`,
`break`/`continue`, loop `else`, nesting, early returns,
`try`/`except`/`else`/`finally`, context managers, and nonlocal exits through
cleanup, with exceptional edges modeled explicitly. Decide from the Part 2
audit whether a bounded CFG/IR layer is needed, and demonstrate the need first.
Every counterexample becomes a permanent minimized regression.

**Gate:** declared control-flow and exception fixtures pass behavioral checks.
Stack and CFG invariants are checked. Independent review is complete.
Unresolved structures are explicitly rejected. Required scope:
`harness/requirements.json` part 6 (`difftest.py gate --part 6`).

## Part 7 — Modern language features and interactions

Comprehensions, generators and `yield from`, `async`/`await`, async
iteration and context managers, `match`, function metadata, annotations,
f-strings and newer string forms. Each is checked against the exact CPython
release. Generator and async fixtures use bounded deterministic drivers.
Interaction matrices cover cases such as closures inside comprehensions and
exceptions inside generators.

**Gate:** required modern-feature fixtures and declared interactions pass on
the applicable versions. Each exclusion has a reproducible example and an
honest diagnostic. No blanket language-support claims. Required scope:
`harness/requirements.json` part 7 (`difftest.py gate --part 7`).

## Part 8 — Harden, document, prepare contributions

Property-based and generated tests with saved seeds and minimization. Fuzzing
under ASan/UBSan with time, memory and recursion limits. Behavioral execution
only for reviewed fixtures and constrained generators. CI across the declared
versions and platforms, with a small required suite and a larger separate
corpus. An independent holdout set. Runtime and memory regression tracking. A
threat model, CLI contract, build docs, support matrix, exclusions and
benchmark methodology. Focused upstream-ready changes with measured
before/after results. No upstream PRs or releases without approval.

**Gate:** CI is green for the required matrix. No new baseline regressions.
Known failures are disclosed. The holdout evaluation is recorded. An
independent model has reviewed the implementation and the evidence. The release
text claims only what was measured.
