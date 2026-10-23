# Feature matrix and required scope

Defined in Part 2, before any decompiler change. The machine-readable source
of truth is `harness/requirements.json`; this page explains it.
**Requirements may be added or tightened. Removing or weakening one requires
an explicit user decision recorded in `docs/DECISIONS.md`.**

Review status: authored by Opus. **Not yet reviewed** by the investigator
role (Kimi K3) or the coordinator (ASTRA); see `docs/HANDOFF.md`.

## How parts are assigned

A fixture belongs to the **highest roadmap part whose constructs it uses**:

- **Part 5** fixtures use only expressions, calls, functions, closures,
  classes and imports. They use no `if`/loops/`try`/`with`,
  `and`/`or`, conditional expressions, chained comparisons,
  comprehensions, generators, f-strings or `match`.
- **Part 6** fixtures may also use branches, short-circuit and conditional
  expressions, loops, `try`/`except`/`finally`, `with` and
  `assert`, but nothing from Part 7.
- **Part 7** fixtures may use anything: comprehensions, generators,
  async, `match`, f-strings, walrus, annotations and version-specific syntax.

This makes each gate meaningful on its own. A Part 5 gate cannot be blocked
by missing loop recovery, and cannot pass by accident either. The fixtures'
directories group them by topic (`category`). The part assignment is
independent of the directory.

## Gate rule per part (`difftest.py gate --part N`)

For every fixture required by Parts 4..N, every **required version** (3.13,
3.14), and every optimization level (0, 1, 2) where the fixture applies:

| Part | Required stage | Fixtures |
| --- | --- | --- |
| 4 | at least `disassemble`: no load or disassembly failure | all features fixtures |
| 5 | `behavior` PASS | 27 fixtures (below) |
| 6 | `behavior` PASS | 19 fixtures |
| 7 | `behavior` PASS | 27 fixtures |

In addition, always:

- no regression against `reports/part2-baseline/baseline.json` in any suite,
  version (3.10–3.14) or optimization level;
- no `MISSING` interpreter and no `HARNESS_ERROR`;
- the harness controls report 0 unexpected outcomes;
- no upstream token-level test file that passed at the Part 1 baseline fails.

For **3.10–3.12** the requirement is *no regression*, not "must pass". This
follows the mission: focus on 3.13/3.14 and keep regression coverage for
3.10–3.12.

Part 4's four decoding requirements were mechanized in Part 4. They are
checked by `gate --decoding DIR` from the reports of
`harness/tools/decoding_check.py`; `requirements.json`, `parts.4.decoding`,
has the exact criteria. Each covers more than the original wording, which
only tightens it:

- **semantic `pycdas`/`dis` agreement:** for the `features`, `decoding` and
  `decoding-generated` suites, on every version 3.10–3.14 (not only 3.13
  and 3.14);
- **hash-based `.pyc` headers:** checked and unchecked, on the same suites
  and versions;
- **clear failure:** for 17 crafted unsupported or undecodable inputs;
- **safe failure on malformed input:**
  - for pycdas on every version;
  - for pycdc on 3.13 and 3.14;
  - pycdc crashes on 3.10–3.12 are reported and must not increase.

## Fixtures

| fixture | part | requires | summary |
| --- | --- | --- | --- |
| `async/async_for_with` | 7 | all | async for over custom async iterators, async with, break/else in async for |
| `async/async_generators` | 7 | all | async generators (asend/athrow/aclose), async comprehensions, await inside comprehensions |
| `async/asyncio_tasks` | 7 | all | asyncio.run with gather, tasks and deterministic interleaving via sleep(0) |
| `async/coroutines` | 7 | all | async def, await on custom awaitables, return values and exceptions driven by a manual loop |
| `branches/conditional_expressions` | 6 | all | conditional expressions, nested and with side effects, in lambdas and call arguments |
| `branches/early_returns` | 6 | all | early returns, implicit None, multiple return points, recursion and mutual recursion |
| `branches/if_elif_else` | 6 | all | if/elif/else chains, nesting, empty bodies, side-effecting conditions, compound conditions |
| `branches/match_literals_captures` | 7 | >=3.10 | match statement with literal, capture, wildcard, value, or/as patterns and guards |
| `branches/match_structures` | 7 | >=3.10 | match with sequence, star, mapping (**rest), class (positional/keyword) and nested patterns |
| `branches/short_circuit` | 6 | all | and/or/not return operands, short-circuit side effects, chained comparisons evaluate once |
| `branches/truthiness` | 6 | all | user-defined __bool__/__len__ call counts in if, while, not, and/or, ternary and assert |
| `calls/arguments` | 5 | all | positional, keyword, defaults, keyword-only, positional-only, *args/**kwargs; a binding error |
| `calls/builtin_calls` | 5 | all | builtins with key functions, map/filter/zip, nested calls, getattr chains |
| `calls/evaluation_order` | 5 | all | evaluation order of callee, arguments, keyword arguments, star-args and chained calls |
| `calls/methods_super` | 5 | all | bound methods, classmethod/staticmethod, zero-arg and explicit super(), method calls on literals |
| `classes/class_basics` | 5 | all | attributes, __init__, inheritance, diamond MRO, class vs instance attributes, properties |
| `classes/class_body_and_nesting` | 5 | all | statements in class bodies, nested classes and qualnames, private name mangling, type() classes |
| `classes/dunder_methods` | 6 | all | container/iteration/call/comparison/hash dunders, NotImplemented fallback, __bool__ via __len__ |
| `classes/metaclasses` | 5 | all | metaclass __prepare__/__new__/__init__ ordering, class keywords, __init_subclass__, __set_name__ |
| `classes/stdlib_class_helpers` | 5 | all | dataclasses, enums, namedtuple and functools.total_ordering used the way real modules use them |
| `closures/class_closures` | 5 | all | __class__ cell and zero-arg super, class body names invisible to methods, classes in functions |
| `closures/closure_basics` | 5 | all | counters with nonlocal, shared cells, late binding vs early binding via defaults |
| `closures/comprehension_closures` | 7 | all | closures created inside comprehensions, comprehensions reading enclosing locals and class scope |
| `closures/nested_scopes` | 5 | all | three-level nesting, free variables passing through intermediate scopes, shadowing |
| `comprehensions/generator_expressions` | 7 | all | generator expression laziness, eager first iterable, short-circuiting consumers |
| `comprehensions/list_set_dict` | 7 | all | list/set/dict comprehensions with filters, nested fors, nested comprehensions, conditionals |
| `comprehensions/scoping` | 7 | all | comprehension variables do not leak, outer names shadowed, nested comprehension scoping |
| `exceptions/assert_statements` | 6 | all | assert with/without message (removed from the compiled program at -O and -OO) |
| `exceptions/call_errors` | 6 | all | argument-binding errors raised by calls (missing, duplicate, positional-only, keyword types) |
| `exceptions/exceptions_in_loops` | 6 | all | try/except inside loops with continue/break/return, exceptions escaping loops |
| `exceptions/import_fallbacks` | 6 | all | optional-import idioms: try/except ImportError at module level and inside functions |
| `exceptions/raise_and_chaining` | 6 | all | raise forms, explicit/implicit chaining, from None, bare re-raise, custom exception classes |
| `exceptions/try_except` | 6 | all | try/except/else/finally, handler order, tuple handlers, bare except, 'as' name unbinding |
| `exceptions/try_finally` | 6 | all | finally on return/break/continue/exception, nested finally order, finally overriding results |
| `exceptions/with_statements` | 6 | all | context manager enter/exit order, exception info to __exit__, suppression, multiple items |
| `expressions/arithmetic` | 5 | all | binary, unary and augmented operators, numeric edge cases, reflected and in-place dunders |
| `expressions/assignment_unpacking` | 5 | all | tuple/starred/nested unpacking, chained assignment aliasing, swaps, subscript augmented order |
| `expressions/attributes` | 5 | all | attribute get/set/del, chains, augmented attribute assignment evaluating the target once |
| `expressions/comparisons` | 5 | all | single comparisons, in/not in, is/is not, rich comparisons returning non-bool values |
| `expressions/delete_statements` | 5 | all | del of names, attributes, subscripts and slices; reading a deleted local raises UnboundLocalError |
| `expressions/fstrings` | 7 | all | f-strings (conversions, format specs, nested specs, = specifier, nesting, concatenation) |
| `expressions/literals` | 5 | all | constants of every type, container displays, starred displays, escapes and folding |
| `expressions/string_formatting` | 5 | all | str.format and printf-style % formatting, string concatenation and repetition |
| `expressions/subscripts_slices` | 5 | all | indexing, slicing with steps, slice assignment/deletion, slice objects passed to __getitem__ |
| `expressions/walrus` | 7 | all | assignment expressions in conditions, loops, comprehensions and call arguments |
| `functions/annotations` | 7 | all | function, variable and class annotations with side effects (eager before 3.14, deferred in 3.14) |
| `functions/decorators` | 5 | all | decorator evaluation and application order, factories, stacking, class decorators |
| `functions/defaults` | 5 | all | default values evaluated once at definition time, mutable default persistence, kw-only defaults |
| `functions/docstrings` | 5 | all | module, class, function and method docstrings (stripped at -OO in the compiled program) |
| `functions/exit_handlers` | 5 | all | atexit handlers run at interpreter exit (observed through the process stdout/stderr channels) |
| `functions/global_nonlocal` | 5 | all | global and nonlocal declarations, module state mutated from functions |
| `functions/lambdas` | 5 | all | lambdas with defaults, varargs, keyword-only args, nesting, immediate calls |
| `generators/generator_cleanup` | 7 | all | GeneratorExit handling, try/finally in generators, exhausted generators, lazy pipelines |
| `generators/generator_protocol` | 7 | all | yield, send, throw, close, return values via StopIteration, finally on close, yield expressions |
| `generators/yield_from` | 7 | all | yield from delegation, return value of yield from, send/throw passthrough, nested delegation |
| `imports/future_annotations` | 7 | all | from __future__ import annotations turns annotations into strings (must be preserved) |
| `imports/import_forms` | 5 | all | import forms with aliases, dotted names, parenthesized from-imports, imports inside functions |
| `imports/import_star` | 5 | all | star import populates module globals (observed through the globals snapshot) |
| `loops/class_body_statements` | 6 | all | loops, conditionals and try statements executed inside class bodies |
| `loops/for_loops` | 6 | all | for/else with and without break, continue, zero iterations, unpacking and attribute targets |
| `loops/iteration_protocol` | 6 | all | custom iterators, StopIteration, iter(callable, sentinel), iteration side-effect order |
| `loops/nested_exits` | 6 | all | breaking out of nested loops via flags/else/return, continue in nested loops, early returns |
| `loops/while_loops` | 6 | all | while/else, break, continue, while True with return, zero iterations, side-effecting conditions |
| `version_specific/deferred_annotations` | 7 | >=3.14 | PEP 649/749 deferred evaluation of annotations, forward references, annotationlib formats |
| `version_specific/except_star` | 7 | >=3.11 | ExceptionGroup and except* (PEP 654): splitting, re-raising unhandled parts, nesting |
| `version_specific/except_without_parens` | 7 | >=3.14 | PEP 758 except clauses listing several types without parentheses |
| `version_specific/exception_notes` | 7 | >=3.11 | BaseException.add_note (PEP 678) and notes on propagated exceptions |
| `version_specific/fstring_pep701` | 7 | >=3.12 | PEP 701 f-strings: reused quotes, backslashes and multi-line expressions inside replacement fields |
| `version_specific/parenthesized_with` | 7 | >=3.10 | parenthesized multi-item with statements (officially 3.10+ grammar) |
| `version_specific/star_subscripts` | 7 | >=3.11 | starred expressions inside subscripts (PEP 646 grammar) |
| `version_specific/template_strings` | 7 | >=3.14 | PEP 750 template string literals (t-strings) |
| `version_specific/type_param_defaults` | 7 | >=3.13 | PEP 696 defaults for type parameters |
| `version_specific/type_params` | 7 | >=3.12 | PEP 695 type parameters on functions/classes and the type statement |

## Explicit exclusions

| Excluded | Why |
| --- | --- |
| source fidelity: comments, formatting, blank lines, choice among equivalent syntax, temporaries' names | not recoverable from bytecode in general; outside the mission |
| everything outside the observation contract (`harness/README.md`): tracebacks, line/column numbers, code-object attributes, object identity, compile-time warnings, timing | deliberate observation-contract exclusions |
| docstrings and `assert` at `-O`/`-OO` | absent from the compiled program; the behavior comparison already accounts for this |
| Python 1.x–3.9 in the behavioral matrix | covered only by upstream's token-level suite, which must not regress |
| Python 3.15+, free-threaded (`t`) builds | outside the agreed version scope |
| adaptive/specialized runtime bytecode | outside the initial scope unless separately approved |
| Cython/Nuitka binaries, packaging extraction, obfuscation | outside the initial scope |
| marshalled code objects (`pycdc -c -v X.Y`) | not in the initial matrix; existing behavior must not regress |
| executing upstream `tests/input` sources | not authored/reviewed fixtures; compiled and decompiled only |

## Known limitations of the matrix (to be addressed, never by removal)

- **Fixtures are deliberately broad.** One unsupported construct fails the
  whole fixture. Parts 5–7 must add a **minimal failing regression fixture
  before each fix** (roadmap rule). Those additions join the required set of
  their part.
- **Opcode coverage of the corpus is not total.**
  `reports/part2-baseline/opcode_coverage.md` lists, per version, every
  opcode the corpus never emits (for example `DELETE_DEREF` and
  `LOAD_FROM_DICT_OR_GLOBALS` on 3.13). Fixtures for emittable ones should be
  added when the relevant part starts.
- **Interaction matrices for Part 7 are small.** They cover closures in
  comprehensions, exceptions thrown into generators and async with
  exceptions. Kimi K3 is expected to extend them adversarially.
- **The behavioral sandbox exists only on macOS.** Linux/CI isolation is a
  Part 8 deliverable.
