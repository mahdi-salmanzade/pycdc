# Differential test results

| | |
| --- | --- |
| created (UTC) | 2026-10-23T02:36:45Z |
| command | `harness/difftest.py run --suite features,upstream-inputs,decoding,decoding-generated --workroot build/part4/official/work --out build/part4/official/results.json --summary build/part4/official/SUMMARY.md` |
| host | macOS-26.7.1-arm64-arm-64bit, harness Python 3.12.2 |
| sandbox | macos-sandbox-exec |
| optimization levels | 0, 1, 2 |
| decompiler source | `a1ae26384c59922b3d7d56410d40b6de1074f05d` (bootstrap), dirty files: none |
| harness | `a1ae26384c59922b3d7d56410d40b6de1074f05d`, dirty files: 0 |
| libpycxx | sha256 `b0c5415e65e56a3599c9cdab4f101fa8685e6956b8db458b806b8356b6b79268` |
| pycdas | sha256 `2b79550224ebfb92a8dc7b6edd58072e7e115f6d894f9814ae3e39fb9452310c` |
| pycdc | sha256 `53f4424166014cdf168485103a6b9340c07f61b1e5095e2ea157391206dd7666` |
| CPython 3.10 | 3.10.22, magic 3439, ok |
| CPython 3.11 | 3.11.17, magic 3495, ok |
| CPython 3.12 | 3.12.15, magic 3531, ok |
| CPython 3.13 | 3.13.17, magic 3571, ok |
| CPython 3.14 | 3.14.9, magic 3627, ok |
| wall time | 43.8s |

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
| compile | 15.4 / 0.085 | 16.4 / 0.084 | 17.6 / 0.085 | 18.0 / 0.085 | 27.6 / 0.139 |
| load | 6.3 / 0.015 | 5.3 / 0.016 | 5.4 / 0.020 | 5.3 / 0.016 | 5.2 / 0.015 |
| disassemble | 6.6 / 0.016 | 5.4 / 0.021 | 5.4 / 0.016 | 5.6 / 0.017 | 5.7 / 0.017 |
| decompile | 6.1 / 0.016 | 5.0 / 0.016 | 5.0 / 0.015 | 5.2 / 0.016 | 5.3 / 0.015 |
| syntax | 12.5 / 0.082 | 13.7 / 0.082 | 14.7 / 0.082 | 15.7 / 0.083 | 16.5 / 0.082 |
| behavior | 13.0 / 0.139 | 13.7 / 0.138 | 11.6 / 0.138 | 30.6 / 0.145 | 36.0 / 0.192 |

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
| compile | 21.1 / 0.083 | 21.6 / 0.083 | 22.4 / 0.084 | 23.9 / 0.086 | 34.5 / 0.141 |
| load | 3.1 / 0.015 | 3.2 / 0.021 | 3.0 / 0.015 | 3.2 / 0.020 | 3.1 / 0.016 |
| disassemble | 3.0 / 0.015 | 3.1 / 0.016 | 3.1 / 0.016 | 3.1 / 0.017 | 3.1 / 0.015 |
| decompile | 3.1 / 0.016 | 3.0 / 0.015 | 3.1 / 0.021 | 3.0 / 0.015 | 3.1 / 0.016 |
| syntax | 11.8 / 0.081 | 11.6 / 0.081 | 11.6 / 0.081 | 11.8 / 0.081 | 12.0 / 0.082 |
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

## Suite `decoding` — validated up to: syntax (not executed)

Every case is counted once, at its earliest failing stage. crash, timeout and incomplete are subsets of the FAIL columns.

| version | cases | PASS | FAIL@load | FAIL@disassemble | FAIL@decompile | FAIL@syntax | FAIL@behavior | crash | timeout | incomplete | N/A | MISSING | HARNESS_ERROR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3.10 | 18 | 0 | 0 | 0 | 6 | 3 | 0 | 0 | 0 | 6 | 9 | 0 | 0 |
| 3.11 | 18 | 0 | 0 | 0 | 9 | 3 | 0 | 0 | 0 | 9 | 6 | 0 | 0 |
| 3.12 | 18 | 0 | 0 | 0 | 12 | 3 | 0 | 0 | 0 | 12 | 3 | 0 | 0 |
| 3.13 | 18 | 0 | 0 | 0 | 15 | 0 | 0 | 0 | 0 | 15 | 3 | 0 | 0 |
| 3.14 | 18 | 0 | 0 | 0 | 18 | 0 | 0 | 0 | 0 | 18 | 0 | 0 | 0 |
| all | 90 | 0 | 0 | 0 | 60 | 9 | 0 | 0 | 0 | 60 | 21 | 0 | 0 |

### PASS / applicable cases by optimization level

| opt | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
| --- | --- | --- | --- | --- | --- |
| -O0 | 0/3 | 0/4 | 0/5 | 0/5 | 0/6 |
| -O1 | 0/3 | 0/4 | 0/5 | 0/5 | 0/6 |
| -O2 | 0/3 | 0/4 | 0/5 | 0/5 | 0/6 |

### Stage wall time in seconds: total / median per case (cases where the stage ran)

behavior times the candidate run only; the reference run is not included.

| stage | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
| --- | --- | --- | --- | --- | --- |
| compile | 1.4 / 0.084 | 1.4 / 0.086 | 1.5 / 0.084 | 1.5 / 0.085 | 2.3 / 0.139 |
| load | 0.1 / 0.014 | 0.2 / 0.015 | 0.3 / 0.014 | 0.3 / 0.015 | 0.4 / 0.024 |
| disassemble | 0.2 / 0.014 | 0.2 / 0.023 | 0.3 / 0.021 | 0.3 / 0.024 | 0.4 / 0.023 |
| decompile | 0.2 / 0.022 | 0.3 / 0.024 | 0.3 / 0.016 | 0.3 / 0.016 | 0.4 / 0.023 |
| syntax | 0.7 / 0.084 | 0.9 / 0.083 | 1.1 / 0.080 | 1.1 / 0.081 | 1.4 / 0.084 |
| behavior | - | - | - | - | - |

### Most frequent failure causes per stage

**decompile** (60 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 27 | incomplete | Unsupported opcode: MAKE_FUNCTION (122) | 3.13, 3.14 |
| 6 | incomplete | Unsupported opcode: MAKE_CELL (229) | 3.11, 3.12 |
| 6 | incomplete | Unsupported opcode: LOAD_SMALL_INT (263) | 3.14 |
| 3 | incomplete | Unsupported opcode: BEFORE_ASYNC_WITH (94) | 3.10 |
| 3 | incomplete | Unsupported opcode: LOAD_FAST_AND_CLEAR (245) | 3.12 |
| 3 | incomplete | Unsupported opcode: POP_JUMP_FORWARD_IF_NOT_NONE (225) | 3.11 |
| 3 | incomplete | Unsupported opcode: POP_JUMP_IF_NOT_NONE (242) | 3.12 |
| 3 | incomplete | Unsupported opcode: CHECK_EG_MATCH (107) | 3.11 |
| 3 | incomplete | Unsupported opcode: LOAD_FAST_CHECK (241) | 3.12 |
| 2 | incomplete | Warning: Stack history is not empty! | 3.10 |
| 1 | incomplete | Unsupported opcode: LOAD_ASSERTION_ERROR (101) | 3.10 |

**syntax** (9 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 9 | syntax_error | SyntaxError: invalid syntax | 3.10, 3.11, 3.12 |

## Suite `decoding-generated` — validated up to: syntax (not executed)

Every case is counted once, at its earliest failing stage. crash, timeout and incomplete are subsets of the FAIL columns.

| version | cases | PASS | FAIL@load | FAIL@disassemble | FAIL@decompile | FAIL@syntax | FAIL@behavior | crash | timeout | incomplete | N/A | MISSING | HARNESS_ERROR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3.10 | 6 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| 3.11 | 6 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 |
| 3.12 | 6 | 0 | 0 | 0 | 3 | 3 | 0 | 0 | 0 | 3 | 0 | 0 | 0 |
| 3.13 | 6 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 |
| 3.14 | 6 | 0 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 |
| all | 30 | 0 | 0 | 0 | 27 | 3 | 0 | 0 | 0 | 24 | 0 | 0 | 0 |

### PASS / applicable cases by optimization level

| opt | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
| --- | --- | --- | --- | --- | --- |
| -O0 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| -O1 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| -O2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |

### Stage wall time in seconds: total / median per case (cases where the stage ran)

behavior times the candidate run only; the reference run is not included.

| stage | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
| --- | --- | --- | --- | --- | --- |
| compile | 1.3 / 0.314 | 1.4 / 0.368 | 1.5 / 0.420 | 1.6 / 0.425 | 1.8 / 0.421 |
| load | 0.2 / 0.046 | 0.2 / 0.045 | 0.2 / 0.041 | 0.2 / 0.038 | 0.2 / 0.037 |
| disassemble | 1.2 / 0.311 | 1.3 / 0.398 | 1.4 / 0.446 | 1.4 / 0.438 | 1.2 / 0.353 |
| decompile | 0.3 / 0.071 | 0.4 / 0.123 | 0.5 / 0.131 | 0.2 / 0.044 | 0.2 / 0.042 |
| syntax | 0.2 / 0.078 | 0.8 / 0.196 | 1.0 / 0.256 | 0.4 / 0.083 | 0.5 / 0.091 |
| behavior | - | - | - | - | - |

### Most frequent failure causes per stage

**decompile** (27 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 6 | incomplete | Unsupported opcode: LIST_TO_TUPLE (102) | 3.10, 3.11 |
| 6 | incomplete | Unsupported opcode: MAKE_FUNCTION (122) | 3.13, 3.14 |
| 3 | incomplete | Unsupported opcode: LOAD_FAST_CHECK (241) | 3.12 |
| 3 | error | PycBuffer::getByte(): Unexpected end of stream | 3.10 |
| 3 | incomplete | Unsupported opcode: POP_JUMP_BACKWARD_IF_TRUE (239) | 3.11 |
| 3 | incomplete | Unsupported opcode: TO_BOOL (123) | 3.13 |
| 3 | incomplete | Unsupported opcode: LOAD_SMALL_INT (263) | 3.14 |

**syntax** (3 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 3 | syntax_error | SyntaxError: 'continue' not properly in loop | 3.12 |

