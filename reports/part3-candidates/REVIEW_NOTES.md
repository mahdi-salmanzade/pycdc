# Code notes on PRs #616 and #617

**Status of these notes.** Opus (the implementation owner) and an Opus
sub-agent wrote them. They are **not** an independent review in the sense
of AGENTS.md. They support D-015; they do not replace the Kimi K3 or ASTRA
review.

Each statement is labelled:
- **[verified]**: reproduced by decompiling an authored probe with the
  candidate build, inside the harness sandbox. Outputs are in `probes/`.
- **[measured]**: from the corpus runs.
- **[read]**: from reading the code only.

Line numbers refer to the PR heads as checked out in `build/part3/src/`.

## Counterexamples verified by execution

The probe sources are `probes/*.py`. Each was compiled with the pinned
interpreter at `-O0` and decompiled by every build. Outputs, including
pycdc's stderr, are in `probes/recovered/<build>/<probe>-<version>.py.txt`.
Nothing was executed except the compiler and pycdc.

In the table, **bold** marks wrong output that carries no incomplete marker
and no diagnostic. "Base" is upstream `b428976`. The integrated build gives
the same output as base on 3.11–3.13; on 3.14 it marks every probe
incomplete.

| Probe | Source | Base | PR #616 | PR #617 |
| --- | --- | --- | --- | --- |
| `ixor.py` | `x ^= y` | 3.11, 3.12: correct. 3.13: incomplete | 3.11, 3.12: **`x = x[y]`**. 3.13, 3.14: correct | 3.11–3.14: correct |
| `bare_yield.py` | `yield`; `x = yield`; `yield None`; `return x` | 3.11–3.13: incomplete | 3.11–3.14: **`x = None` / `return x`**; every `yield` is dropped, so `g` is no longer a generator | 3.11–3.14: incomplete (`RETURN_GENERATOR`) |
| `except_store.py` | `except ValueError: x = 1; return x` | 3.11: **`return` instead of `return x`** (an older upstream bug). 3.12: the same output, plus a diagnostic. 3.13: incomplete | 3.11–3.14: **`except ValueError as x: return x`** | 3.11: as base. 3.12–3.14: wrong `return`/`return None`, plus a diagnostic |
| `decorator_order.py` | `@deco(print('a'))` on `def f(x=print('b'))` | 3.11, 3.12: **`f = (lambda x = (print('b'),): x)()`**; the decorator and `print('a')` are lost, and the result is a call (an older upstream bug). 3.13: incomplete | 3.11, 3.12: as base. 3.13, 3.14: **`f = (lambda x = print('b'): x)()`** | 3.11, 3.12: as base. 3.13, 3.14: **`def f(x = print('b'))` then `f = deco(print('a'))(f)`**; `b` would print before `a`, and `f` is briefly bound undecorated |

**Implications for the corpus.**
- #616's `x ^= y` → `x = x[y]` regression on 3.11/3.12 was **not** caught
  by the behavioral corpus: no feature fixture uses `^=` in code that those
  versions decompile.
- Upstream itself silently mis-decompiles two of the four probes on
  3.11/3.12. These are older bugs, not caused by either PR.
- Proposed fixture additions, for Kimi K3 to review:
  - augmented assignment for each operator;
  - bare `yield` and `x = yield`;
  - a plain store and a return inside an `except` arm;
  - decorator and default-value evaluation order.
- The corpus may only grow; a new corpus version needs a recorded
  decision.

## PR #616

### Size and structure [read]

- One commit, +4419/−81. `BuildFromCode` grows from about 2,650 to about
  5,370 lines.
- It adds 26 look-ahead copies of the bytecode stream (base has none) and a
  `PycBuffer::setPos` with no bounds check (`data.h:55`). `atEof()` tests
  `m_pos == m_size`, so a misaligned or past-the-end position never reports
  end of stream; reads are bounded only by `pos + 0x10000`.
- It also rewinds or skips the main stream:
  - `source = probe` / `saved_src`;
  - skip loops;
  - a blind four-instruction skip at 4593.
- The conditional-jump opcode list is duplicated at least five times, each
  with its own target arithmetic.

### Changes that reach versions it does not target [read, partly verified]

- **`BINARY_OP` subscript path** is gated `operand == 25 && 3.11 <= v < 3.13`
  (1162–1163). In 3.11–3.13 operand 25 is in-place XOR (`^=`); the subscript
  operand (26) exists only in 3.14. **[verified]** by `ixor.py`.
- **`YIELD_VALUE`** with a None value (5222–5227) is ungated and drops the
  yield. **[verified]** by `bare_yield.py`.
- **First `STORE_FAST` in an except arm** becomes the `as` target
  (4874–4880). **[verified]** by `except_store.py`.
- **`JUMP_FORWARD`** offset is made absolute for 3.10+ (3179–3187). Older
  uses still compare `offs == 0` (3291, 3307) and compute `pos + offs`
  (3334, 3348), which now counts `pos` twice. [read]
- **Ungated changes:**
  - `RETURN_VALUE` consumes the next instruction only if it is a jump
    (4389–4402, every version from 2.6);
  - the `CALL` `__exit__`-epilogue heuristic (1564–1623) shares
    `CALL_FUNCTION_A`'s path;
  - also `BUILD_MAP` order, `DICT_MERGE`/`DICT_UPDATE`, `CALL_FUNCTION_EX_A`
    and `SET_ADD`/`MAP_ADD`. [read]
- **[measured]** 61 new silent mismatches on 3.10–3.12.

### How the incomplete marker is bypassed [read]

- **No-op or partial handlers** for opcodes that used to reach the switch
  `default:`:
  - `CALL_INTRINSIC_1` treats every intrinsic as a no-op (5259–5264), so
    `+x`, `import *` and list-to-tuple are mis-rendered;
  - `RETURN_GENERATOR`, `SEND`, `JUMP_BACKWARD_NO_INTERRUPT`,
    `CLEANUP_THROW` and `CHECK_EG_MATCH` are absorbed, and `except*` is
    printed as `except` (4009–4019);
  - `SET_FUNCTION_ATTRIBUTE` silently drops annotations (3890).
- **Silent instruction skips:**
  - `with` epilogues, sometimes the rest of the code object (589–592);
  - re-raise regions;
  - comprehension handlers;
  - dead loop-back regions.
- **Lost blocks at the end.** With `while_else_exit` set, the end of
  `BuildFromCode` (5498) skips both the "block stack is not empty" warning
  and the re-attachment of open blocks, so their statements disappear.
- **Unmasking.** Newly decoded opcodes (`LOAD_ASSERTION_ERROR`,
  `DICT_MERGE`, `CALL_FUNCTION_EX_A`) remove the marker from code objects
  that still contain older reconstruction bugs. The `memo=({},)` default bug
  is one: `MAKE_FUNCTION_A` is unchanged (3795–3806), while the new 3.13
  path unpacks defaults correctly (3852–3854).

### Crashes and hangs

- **[measured] Crash on `loops/nested_exits`.**
  - Seen on 3.12, 3.13 and 3.14, at every `-O` level.
  - Across two runs it died with SIGSEGV, SIGBUS, or an uncaught C++
    `std::vector` exception. That variation is consistent with memory
    corruption.
  - **[read] Hypotheses:**
    - `std::stack::top()`/`pop()` on an empty `stack_hist`; ELSE blocks are
      pushed without a history entry (3046–3049, 4066–4072), and older
      unguarded pops are now reachable (e.g. 3089–3090);
    - or re-mounting pending containers creates a cycle (963–998).
- **[measured] Hang in `loops/iteration_protocol` (3.13, 3.14).**
  - Shape: `while True: try: v = next(it) except StopIteration: break`.
  - [read] The deferred handler container turns the handler's backward
    `break` jump into `continue` (3102–3104), so the recovered loop never
    ends.
- **[measured] Hang in `branches/truthiness` (3.12).**
  - [read] An `if not v: continue` inside `while True` is recognized as a
    nested `while` (2481–2786), giving `while not v: pass`.

### Separable pieces [read]

**Low risk alone:**
- slice marshal support (adopted, via #596);
- the 3.14 magic and opcode table (adopted);
- pycdas jump-target display (Part 4 candidate; changes 3.12/3.13 pycdas
  output and must be checked against `dis`);
- trivial loads and no-op opcodes;
- 3.13 f-string opcodes and `CALL_KW`;
- `MAKE_FUNCTION`/`SET_FUNCTION_ATTRIBUTE`, if annotations are made
  explicit;
- `BUILD_MAP` order.

**Entangled:**
- the exception-table rewrite with pending containers;
- all loop recovery;
- the inline-comprehension state machine;
- `with` modelling;
- the 3.12+ conditional-jump heuristics;
- the ungated changes listed above.

## PR #617

### Structure [read]

- One commit, +838/−23. Most changes are gated 3.13+ or 3.14+.
- **Unsupported shapes throw `std::runtime_error`, so pycdc exits nonzero:**
  general `DICT_MERGE`, class keywords, lazy annotations
  (`SET_FUNCTION_ATTRIBUTE` 16), crossing short circuits, and an invalid
  `SWAP`.
- The circular-reference guard in `print_src`/`decompyle` becomes a
  recursion-path set that throws, instead of a global "seen" set that
  printed a warning and returned. This changes behavior for every version.

### Look-ahead heuristics [read]

- **Short-circuit reconstruction:** a `PycBuffer` probe over
  `CACHE`/`NOT_TAKEN` to a `POP_TOP`, plus a pending `short_circuits`
  stack applied when `pos` reaches the recorded end.
- **Consecutive `STORE_FAST`s** become one tuple assignment, so that values
  evaluated before their stores keep their order. This is gated to 3.13+;
  unpacking, chained stores and uninitialized `for` blocks are excluded.
- **`RETURN_VALUE`** consumes the following instruction only if it is a
  `JUMP_FORWARD`. This is ungated, so it changes every version.
- **`POP_BLOCK` with only the root block left** is silently ignored.

### Semantics

- **`call_argument`:** decorators and non-lambda function arguments become
  `name = function` before the call. **[verified]** by
  `decorator_order.py`: function creation, including default values, moves
  ahead of the decorator expression.
- **[measured] Crash on `branches/short_circuit` (3.13, 3.14).** SIGSEGV;
  not analyzed further.
- **[measured] 3.14 slice constants fail to load.** Six feature and six
  upstream-input cases fail with `CreateObject: Got unsupported type 0x3A`.
