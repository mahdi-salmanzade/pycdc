# Differential test results

| | |
| --- | --- |
| created (UTC) | 2026-10-23T01:42:45Z |
| command | `harness/difftest.py run --suite features,upstream-inputs --workroot build/part3/work-integrated --out reports/part3-candidates/integrated.json --summary reports/part3-candidates/integrated.SUMMARY.md` |
| host | macOS-26.7.1-arm64-arm-64bit, harness Python 3.12.2 |
| sandbox | macos-sandbox-exec |
| optimization levels | 0, 1, 2 |
| decompiler source | `27ef3c6700df5a356bfc356ee6ff178413a12301` (bootstrap), dirty files: none |
| harness | `27ef3c6700df5a356bfc356ee6ff178413a12301`, dirty files: 0 |
| libpycxx | sha256 `498b9beca9e56dccabc89c95db7c0cdd8903812f3b6f22d9c72464e750ae2dbc` |
| pycdas | sha256 `8ede6a8cb957c58f519d6ebfb32d36d12b978fb570b51dc3e5b0047654a43f4b` |
| pycdc | sha256 `6d542cc6acd6ac715ec3ce9cec9d215df6ffb5ad216e1e5037a9b2278101d979` |
| CPython 3.10 | 3.10.22, magic 3439, ok |
| CPython 3.11 | 3.11.17, magic 3495, ok |
| CPython 3.12 | 3.12.15, magic 3531, ok |
| CPython 3.13 | 3.13.17, magic 3571, ok |
| CPython 3.14 | 3.14.9, magic 3627, ok |
| wall time | 45.5s |

## Suite `features` — validated up to: behavior

Every case is counted once, at its earliest failing stage. crash, timeout and incomplete are subsets of the FAIL columns.

| version | cases | PASS | FAIL@load | FAIL@disassemble | FAIL@decompile | FAIL@syntax | FAIL@behavior | crash | timeout | incomplete | N/A | MISSING | HARNESS_ERROR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3.10 | 219 | 15 | 0 | 0 | 126 | 15 | 36 | 6 | 0 | 93 | 27 | 0 | 0 |
| 3.11 | 219 | 15 | 0 | 0 | 165 | 6 | 15 | 3 | 0 | 124 | 18 | 0 | 0 |
| 3.12 | 219 | 9 | 0 | 0 | 175 | 11 | 12 | 0 | 0 | 142 | 12 | 0 | 0 |
| 3.13 | 219 | 0 | 0 | 0 | 210 | 0 | 0 | 0 | 0 | 210 | 9 | 0 | 0 |
| 3.14 | 219 | 0 | 0 | 0 | 219 | 0 | 0 | 0 | 0 | 219 | 0 | 0 | 0 |
| all | 1095 | 39 | 0 | 0 | 895 | 32 | 63 | 9 | 0 | 788 | 66 | 0 | 0 |

### PASS / applicable cases by category (all optimization levels)

| category | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
| --- | --- | --- | --- | --- | --- |
| async | 0/12 | 0/12 | 0/12 | 0/12 | 0/12 |
| branches | 0/21 | 0/21 | 0/21 | 0/21 | 0/21 |
| calls | 0/12 | 0/12 | 0/12 | 0/12 | 0/12 |
| classes | 0/15 | 0/15 | 0/15 | 0/15 | 0/15 |
| closures | 0/12 | 0/12 | 0/12 | 0/12 | 0/12 |
| comprehensions | 0/9 | 0/9 | 0/9 | 0/9 | 0/9 |
| exceptions | 0/24 | 0/24 | 0/24 | 0/24 | 0/24 |
| expressions | 6/30 | 9/30 | 6/30 | 0/30 | 0/30 |
| functions | 6/21 | 3/21 | 3/21 | 0/21 | 0/21 |
| generators | 0/9 | 0/9 | 0/9 | 0/9 | 0/9 |
| imports | 3/9 | 3/9 | 0/9 | 0/9 | 0/9 |
| loops | 0/15 | 0/15 | 0/15 | 0/15 | 0/15 |
| version_specific | 0/3 | 0/12 | 0/18 | 0/21 | 0/30 |

### PASS / applicable cases by optimization level

| opt | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
| --- | --- | --- | --- | --- | --- |
| -O0 | 5/64 | 5/67 | 3/69 | 0/70 | 0/73 |
| -O1 | 5/64 | 5/67 | 3/69 | 0/70 | 0/73 |
| -O2 | 5/64 | 5/67 | 3/69 | 0/70 | 0/73 |

### Stage wall time in seconds: total / median per case (cases where the stage ran)

behavior times the candidate run only; the reference run is not included.

| stage | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
| --- | --- | --- | --- | --- | --- |
| compile | 19.8 / 0.123 | 20.4 / 0.080 | 22.8 / 0.128 | 23.6 / 0.127 | 32.3 / 0.181 |
| load | 8.7 / 0.022 | 6.6 / 0.022 | 6.7 / 0.022 | 6.7 / 0.022 | 6.8 / 0.022 |
| disassemble | 4.3 / 0.022 | 4.4 / 0.022 | 4.6 / 0.022 | 4.6 / 0.022 | 4.9 / 0.022 |
| decompile | 4.2 / 0.022 | 4.5 / 0.022 | 4.6 / 0.022 | 4.6 / 0.022 | 4.8 / 0.022 |
| syntax | 11.9 / 0.076 | 13.2 / 0.076 | 13.8 / 0.075 | 16.6 / 0.077 | 19.4 / 0.078 |
| behavior | 13.8 / 0.131 | 14.7 / 0.130 | 12.5 / 0.131 | 35.8 / 0.183 | 37.2 / 0.182 |

### Most frequent failure causes per stage

**decompile** (895 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 372 | incomplete | Unsupported opcode: MAKE_FUNCTION (122) | 3.13, 3.14 |
| 99 | incomplete | Unsupported opcode: MAKE_CELL (229) | 3.11, 3.12, 3.14 |
| 51 | incomplete | Unsupported opcode: RETURN_GENERATOR (109) | 3.11, 3.12 |
| 48 | incomplete | Unsupported opcode: LOAD_SMALL_INT (263) | 3.14 |
| 35 | incomplete | Unsupported opcode: JUMP_IF_NOT_EXC_MATCH (214) | 3.10 |
| 24 | incomplete | Unsupported opcode: CALL_FUNCTION_EX (174) | 3.10, 3.11, 3.12 |
| 21 | diagnostic | Warning: Stack history is not empty! | 3.11, 3.12 |
| 21 | diagnostic | Something TERRIBLE happened! | 3.11, 3.12 |
| 18 | error | Unsupported argument found for LIST_EXTEND | 3.10, 3.11, 3.12 |
| 12 | incomplete | Warning: block stack is not empty! | 3.10, 3.11 |
| 12 | incomplete | Unsupported opcode: UNPACK_EX (193) | 3.10, 3.11, 3.12 |
| 9 | incomplete | Unsupported opcode: POP_JUMP_FORWARD_IF_NOT_NONE (225) | 3.11 |
| … | | 28 more distinct causes | |

**syntax** (32 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 17 | syntax_error | SyntaxError: invalid syntax | 3.10, 3.11, 3.12 |
| 3 | syntax_error | SyntaxError: 'None' is an illegal expression for augmented assignment | 3.10 |
| 3 | syntax_error | SyntaxError: 'continue' not properly in loop | 3.12 |
| 3 | syntax_error | SyntaxError: invalid decimal literal | 3.10 |
| 3 | syntax_error | SyntaxError: invalid syntax. Maybe you meant '==' or ':=' instead of '='? | 3.10 |
| 3 | syntax_error | SyntaxError: * argument may appear only once | 3.11 |

**behavior** (63 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 18 | mismatch | observe.outcome | 3.10, 3.11, 3.12 |
| 15 | mismatch | globals.outcome, observe.outcome | 3.10, 3.11, 3.12 |
| 12 | mismatch | module.outcome, globals.outcome, observe.transcript, observe.outcome, observe.present | 3.10, 3.11, 3.12 |
| 9 | mismatch | observe.transcript, observe.outcome | 3.10, 3.11 |
| 9 | mismatch | module.transcript, globals.outcome, observe.outcome | 3.10, 3.11, 3.12 |

## Suite `upstream-inputs` — validated up to: syntax (not executed)

Every case is counted once, at its earliest failing stage. crash, timeout and incomplete are subsets of the FAIL columns.

| version | cases | PASS | FAIL@load | FAIL@disassemble | FAIL@decompile | FAIL@syntax | FAIL@behavior | crash | timeout | incomplete | N/A | MISSING | HARNESS_ERROR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3.10 | 270 | 135 | 0 | 0 | 21 | 9 | 0 | 0 | 0 | 18 | 105 | 0 | 0 |
| 3.11 | 270 | 114 | 0 | 0 | 42 | 9 | 0 | 3 | 0 | 27 | 105 | 0 | 0 |
| 3.12 | 270 | 120 | 0 | 0 | 33 | 12 | 0 | 0 | 0 | 27 | 105 | 0 | 0 |
| 3.13 | 270 | 66 | 0 | 0 | 90 | 9 | 0 | 0 | 0 | 84 | 105 | 0 | 0 |
| 3.14 | 270 | 15 | 0 | 0 | 150 | 0 | 0 | 0 | 0 | 147 | 105 | 0 | 0 |
| all | 1350 | 450 | 0 | 0 | 336 | 39 | 0 | 3 | 0 | 303 | 525 | 0 | 0 |

### PASS / applicable cases by optimization level

| opt | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
| --- | --- | --- | --- | --- | --- |
| -O0 | 45/55 | 38/55 | 40/55 | 22/55 | 5/55 |
| -O1 | 45/55 | 38/55 | 40/55 | 22/55 | 5/55 |
| -O2 | 45/55 | 38/55 | 40/55 | 22/55 | 5/55 |

### Stage wall time in seconds: total / median per case (cases where the stage ran)

behavior times the candidate run only; the reference run is not included.

| stage | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
| --- | --- | --- | --- | --- | --- |
| compile | 26.2 / 0.079 | 26.7 / 0.079 | 28.4 / 0.125 | 29.9 / 0.128 | 38.1 / 0.178 |
| load | 3.4 / 0.022 | 3.4 / 0.022 | 3.5 / 0.022 | 3.5 / 0.022 | 3.4 / 0.022 |
| disassemble | 3.6 / 0.022 | 3.4 / 0.022 | 3.5 / 0.022 | 3.5 / 0.022 | 3.6 / 0.022 |
| decompile | 3.5 / 0.022 | 3.4 / 0.022 | 3.5 / 0.022 | 3.5 / 0.022 | 3.6 / 0.022 |
| syntax | 10.7 / 0.074 | 10.6 / 0.075 | 10.8 / 0.075 | 12.2 / 0.076 | 13.3 / 0.077 |
| behavior | - | - | - | - | - |

### Most frequent failure causes per stage

**decompile** (336 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 141 | incomplete | Unsupported opcode: MAKE_FUNCTION (122) | 3.13, 3.14 |
| 72 | incomplete | Unsupported opcode: LOAD_SMALL_INT (263) | 3.14 |
| 24 | incomplete | Unsupported opcode: RETURN_GENERATOR (109) | 3.11, 3.12 |
| 21 | incomplete | Unsupported opcode: MAKE_CELL (229) | 3.11, 3.12, 3.14 |
| 12 | diagnostic | Warning: block stack is not empty! | 3.11 |
| 12 | diagnostic | Warning: Stack history is not empty! | 3.10, 3.12, 3.13 |
| 9 | incomplete | Unsupported opcode: JUMP_IF_NOT_EXC_MATCH (214) | 3.10 |
| 9 | incomplete | Warning: Stack history is not empty! | 3.10, 3.12 |
| 6 | incomplete | Unsupported opcode: POP_JUMP_BACKWARD_IF_TRUE (239) | 3.11 |
| 3 | incomplete | Unsupported use of GET_AITER outside of SETUP_LOOP | 3.10 |
| 3 | diagnostic | Unsupported `BINARY_OP` operand value: 26 | 3.14 |
| 3 | incomplete | Unsupported opcode: FORMAT_SIMPLE (120) | 3.13 |
| … | | 7 more distinct causes | |

**syntax** (39 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 36 | syntax_error | SyntaxError: 'return' outside function | 3.10, 3.11, 3.12, 3.13 |
| 3 | syntax_error | SyntaxError: 'continue' not properly in loop | 3.12 |

