# pycdc architecture audit (Part 2)

This is the decompilation pipeline as it exists at upstream `b4289760970d`.
Every claim cites `file:line`.

**Provenance.**
- The map comes from a source-reading audit done by an Opus sub-agent, the same
  model family as the implementation owner. **It is not an independent
  review.**
- Claims marked **[verified]** were re-read in the source by the author of this
  document, or confirmed by executing the harness. Unmarked claims come from
  reading only.
- The opcode-level numbers come from `reports/part2-baseline/opcode_coverage.md`
  (generated, see below), not from reading.

## Pipeline

```
.pyc ─► PycModule::loadFromFile ─► LoadObject / CreateObject ─► PycCode::load
        (pyc_module.cpp)           (pyc_object.cpp, data.cpp)    (pyc_code.cpp)
                                                                     │
    pycdas: output_object ─► bc_disasm (bytecode.cpp) ◄──────────────┤
                                                                     ▼
    pycdc:  decompyle (ASTree.cpp:3586) ─► BuildFromCode (ASTree.cpp:76-2728)
              opcode decode: bc_next (bytecode.cpp:279) + bytes/python_X_Y.cpp
              operand stack: FastStack.h; block stack: ASTBlock (ASTNode.h:530)
            ─► AST (ASTNode.h) ─► print_src (ASTree.cpp) ─► source text
```

### 1. Entry points

**pycdc**
- `pycdc.cpp:12-104`. Writes the source to stdout, or to the file given with `-o`.
- Exits 1 on a load error, an invalid module or an exception during decompilation.
- **Exits 0 even when the output contains the incomplete marker, or when
  diagnostics were printed to stderr [verified].**

**pycdas**
- `pycdas.cpp:262-359`. It never calls `isValid()` after loading [verified].
- After a bad magic it prints `<name> (Python -1.-1)` and `<NULL>`, and exits 0
  (`pycdas.cpp:82-85, 347-358`) [verified for `<NULL>`].
- This is why the harness has a separate load probe.
- *Update, Part 4 (`cf86619`):* pycdas now checks the load and exits 1 with
  "Could not load file". An unknown marshal type code now fails in both
  tools instead of returning NULL. Verified by
  `decoding_check.py formats`.

### 2. Loading

- **Magic constants** go up to `MAGIC_3_13` (`pyc_module.h:7-41`). An unknown
  magic sets the version to -1.-1, prints `Bad MAGIC!` and returns
  (`pyc_module.cpp:186-217`) [verified].
- **3.14 has no magic entry**, so every 3.14 file fails at the load stage
  [verified by execution].
  - *Update, Part 3 (`27ef3c6`):* `MAGIC_3_14` (3627) was added; 3.14 files
    now load. See D-015.
- **Header (3.7+):** a flags word is read. If `flags & 1`, the 8-byte hash is
  skipped; otherwise the timestamp and size are skipped
  (`pyc_module.cpp:219-232`) [verified].
- `loadFromMarshalledFile` (`-c -v X.Y`) accepts only versions up to 3.12
  (`pyc_module.cpp:192-204`) [verified].

### 3. Marshal and code objects

- **End of stream:** `PycFile` and `PycBuffer` print a message and call
  `std::exit(1)` (`data.cpp:53-93`) [verified].
  - The process exits in the middle of a run, and `PycBuffer` is also used for
    bytecode.
  - The baseline records 15 decompile-stage cases with
    `PycBuffer::getByte(): Unexpected end of stream` [verified by execution].
- **Unsupported marshal type codes:** `CreateObject` prints a message and
  returns NULL without consuming the object (`pyc_object.cpp:66-68`), so the
  rest of the stream is misparsed.
  - *Update, Part 3 (`200a4cd`):* the 3.14 slice constant (`TYPE_SLICE`,
    `':'`) is now supported (`PycSlice`, `pyc_sequence.h`).
- **Code-object layout** per version: `pyc_code.cpp:29-120`, with the table in
  the comments at 5-27.
  - qualname and exceptiontable are read for 3.11+.
  - localsplusnames/kinds replace varnames/cellvars/freevars in 3.11+.

### 4. Opcode decoding

- **Tables:** raw opcodes map through `bytes/python_X_Y.cpp`
  (`MAP_OP(raw, Name)`) to the internal `Pyc::` enum (`bytecode_ops.inl`).
  Unmapped values become `PYC_INVALID_OPCODE`.
- **Table accuracy, measured:** for 3.10–3.13, every opcode that CPython can
  write to disk is mapped to the correct raw number. There are no wrong or
  extra entries. There is no 3.14 table (`opcode_coverage.md`).
  - *Update, Part 3 (`27ef3c6`):* `bytes/python_3_14.cpp` maps all 121
    on-disk 3.14.9 opcodes correctly
    (`reports/part3-candidates/opcode_coverage.md`). `BuildFromCode` has no
    3.14-specific cases, so 3.14 code stops explicitly at the first
    unsupported opcode.
- **Decoding** (`bc_next`, `bytecode.cpp:279-303`):
  - From 3.6 on (wordcode), only **one** `EXTENDED_ARG` prefix is folded into
    the operand.
    - *Update, Part 4 (`cb77d0b`):* all consecutive prefixes are now folded.
  - CACHE units are decoded as separate `CACHE` instructions, which the switch
    then ignores.
- **Disassembly jump targets:** `bc_disasm` handles jump-target arithmetic per
  version. A TODO at `bytecode.cpp:475-478` notes that CACHE entries are not
  accounted for.
  - *Update, Part 4 (`cc7cf1f`):* pycdas counts relative jumps from the end
    of the inline caches (`bc_skip_caches`), and 3.11 `JUMP_IF_*_OR_POP`
    are relative.
  - The AST builder's own jump arithmetic is unchanged (D-018).
- **Constant rendering** (`print_const`, `PycString::print`), shared by
  pycdas and the decompiler:
  - **Before Part 4:** floats used `%g` (`2.0` became `2`, `-0.0` became
    `0`, six digits). Python 3 interned strings were escaped as bytes
    (`'é'` became `'\xc3\xa9'`).
  - *Update, Part 4 (`d8f80f3`, `315bd39`):* exact float and complex
    rendering; interned strings are printed as text; surrogates and
    invisible or bidi code points are escaped.
- **Verified:** `harness/tools/decoding_check.py dis` compares pycdas with
  `dis` on every corpus file (`reports/part4-decoding/`).

### 5. AST construction (`BuildFromCode`, `ASTree.cpp:76-2728`)

**The main loop.** A single loop over instructions drives a 181-case `switch`
on the internal opcode.

**State.** The loop keeps an operand stack (`FastStack`), a history of whole
stack copies (`stack_hist`) for branches, and a block stack: if, else, elif,
while, for, try, except, finally, with, async-for and container blocks.

**Unsupported opcode** [verified, `ASTree.cpp:2695-2698`]:
- The switch default prints `Unsupported opcode: NAME (n)` and sets
  `cleanBuild = false`.
- It **returns at once**, with only the statements finished so far.
- Open blocks and pending stack values are discarded.
- The caller then prints the incomplete marker.

**Stack underflow** [verified, `FastStack.h:29-52`]:
- `pop` on an empty stack is silent, and `top()` returns `nullptr`.
- `nullptr` is also how the code represents `None`, the NULL that
  `PUSH_NULL` pushes, and the NULL bits of `LOAD_GLOBAL`/`LOAD_ATTR`.
- So an underflow can silently print as `None`. The baseline contains
  recovered code such as `None(out.append if ...)` [verified by execution].

**Loops:**
- `while` blocks are created **only** by `SETUP_LOOP` (`ASTree.cpp:2085-2091`;
  `BLK_WHILE` appears nowhere else) [verified].
- That opcode does not exist from 3.8 on, so 3.8+ `while` loops have no
  dedicated reconstruction.
- `for` blocks come from `FOR_ITER` (`ASTree.cpp:981-1020`).

**3.11+ exceptions:**
- The exception-table entries open try/except blocks only when the stack is
  empty at the start of the entry and `lasti` is not set
  (`ASTree.cpp:117-193`).
- Containers are created without `finally` (`:130`).

**Known logic hazards found by reading:**

| Location | Hazard |
| --- | --- |
| `ASTree.cpp:1255-1266` [verified] | `JUMP_BACKWARD` shares the `JUMP_ABSOLUTE` case. The relative operand times 2 is compared as if it were an absolute offset. |
| `ASTree.cpp:1945-1957` [verified] | `RETURN_VALUE` inside an if/else block (2.6+) consumes the **next** instruction with an extra `bc_next`, without checking what it skipped. |
| `ASTree.cpp:1665-1666` [verified] | `MAKE_FUNCTION` decodes its operand with the pre-3.6 layout (default and kw-default counts) instead of the 3.6+ flags. Execution shows the effect: `def f(bucket=[])` comes out as `bucket = ([],)`, closures gain fake defaults (`def who(self = None)`), and keyword-only defaults are lost [effect verified by execution]. |
| `ASTree.cpp:3273, 3285` [verified] | The import-alias check compares `const char*` pointers (`PycString::value()`, `pyc_string.h:25`). Execution shows `import os.path` emitted as `import os.path as os` and `import collections.abc as cabc` as `from collections.abc import abc as cabc` [effect verified by execution]. |
| 3.11+ `except X as e:` | Recovered as `except X:` followed by `e = None` [effect verified by execution]. |
| `stack_hist.top()` | Called without an emptiness check at several sites (e.g. `:899, :924, :1195`). This is undefined behavior on an empty `std::stack`. |
| Global mutable state | `cleanBuild`, `cur_indent`, `inLambda`, `printDocstringAndGlobals`, `printClassDocstring`, `code_seen`, `node_seen` (`ASTree.cpp`). Name unmangling rewrites shared `PycString` objects in place (`:2353-2356`) [verified]. |

### 6. Source emission (`print_src`, `decompyle`, `ASTree.cpp:2828-3689`)

**Nested code objects** (functions, lambdas, classes) are printed by recursing
into `decompyle` (`:3173-3183`).

**Incomplete marker** [verified, `ASTree.cpp:3659-3686`]:
- The marker `# WARNING: Decompyle incomplete` is emitted only when the
  **current code object's** `BuildFromCode` hit the unsupported-opcode path.
- An `Unsupported Node type` during printing emits `<NODE:n>` with no marker.

**Comprehensions:**
- Comprehensions are rebuilt from `LIST_APPEND` within a comprehension
  `for` block (`:1492-1509`). A code object counts as a comprehension only if
  it is named `<listcomp>` (`:997-1002`).
- No code inlines 3.12+ comprehensions (PEP 709 inlined them into the caller).

### 7. Tests

- **`tests/run_tests.py`:** token-level comparison of the output with
  `tests/tokenized/*.txt`. Any stderr output or a nonzero exit fails a test.
- **`scripts/token_dump`:** skips comment lines (`:180-201`) [verified], so
  the incomplete marker itself is invisible to the token comparison. Only the
  accompanying stderr message makes the test fail.
- **Corpus:** 191 compiled and 39 xfail `.pyc` files; none for 3.13 or 3.14
  (Part 1).

## Measured opcode coverage (feature corpus, all `-O` levels)

From `reports/part2-baseline/opcode_coverage.md`:

| Version | On-disk CPython opcodes | Table correct | Handled by the AST switch | Used by corpus | Used but unhandled |
| --- | --- | --- | --- | --- | --- |
| 3.10 | 127 | 127 | 105 | 123 | 20 |
| 3.11 | 110 | 110 | 78 | 106 | 28 |
| 3.12 | 111 | 111 | 75 | 107 | 32 |
| 3.13 | 118 | 118 | 72 | 113 | 41 |
| 3.14 | 121 | 0 (no table) | 0 | 116 | 116 |

After Part 3 (`27ef3c6`, `reports/part3-candidates/opcode_coverage.md`), 3.14
maps 121 of 121 correctly; 68 are handled by the AST switch, and 50 opcodes
are used by the corpus but unhandled. 3.10–3.13 are unchanged.

## Implications for later parts

These are hypotheses for ASTRA to rule on, not decisions.

1. **3.14 (Part 4)** needs a magic value, a code-object layout check and an
   opcode table before anything else can be measured.
2. **Decoding is not the bottleneck for 3.10–3.13**; the tables are correct.
   Failures concentrate in `BuildFromCode`: unhandled opcodes, and a few
   cross-version operand-layout errors such as `MAKE_FUNCTION`.
3. **Loop and branch recovery for 3.8+** rely on jump-pattern heuristics
   without a `while`-block construct, and on a mis-scaled `JUMP_BACKWARD`.
   - The Part 6 audit question is whether these can be fixed locally or need
     a bounded CFG layer.
   - Part 6 requires that need to be demonstrated before it is built.
4. **Silent failure modes** exist: stack underflow printed as `None`, dropped
   instructions, and a marker that covers only unsupported opcodes. That makes
   behavioral checking mandatory. A clean exit plus syntax-valid output is not
   evidence of success.
