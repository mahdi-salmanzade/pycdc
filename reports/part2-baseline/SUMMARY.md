# Differential test results

| | |
| --- | --- |
| created (UTC) | 2026-10-22T20:10:21Z |
| command | `harness/difftest.py run --suite features,upstream-inputs --out reports/part2-baseline/baseline.json --summary reports/part2-baseline/SUMMARY.md` |
| host | macOS-26.7.1-arm64-arm-64bit, harness Python 3.12.2 |
| sandbox | macos-sandbox-exec |
| optimization levels | 0, 1, 2 |
| decompiler source | `afc500098e2b7fe2c64e1ef4b821a931495b7f3f` (bootstrap), dirty files: none |
| harness | `afc500098e2b7fe2c64e1ef4b821a931495b7f3f`, dirty files: 0 |
| libpycxx | sha256 `582e0e49feb6a641a4e07532e0a9c89b1bad87f1bdb94a11a78067c34c80fbf3` |
| pycdas | sha256 `9c113e5bba7a4c520f1cf4a52e84cfdd47d460d46c3ebd5a48485ca23163df33` |
| pycdc | sha256 `8c0e1d265da12bd37e266a88422e410ed380ce8643e53e935c06897b94a8b2f0` |
| CPython 3.10 | 3.10.22, magic 3439, ok |
| CPython 3.11 | 3.11.17, magic 3495, ok |
| CPython 3.12 | 3.12.15, magic 3531, ok |
| CPython 3.13 | 3.13.17, magic 3571, ok |
| CPython 3.14 | 3.14.9, magic 3627, ok |
| wall time | 40.0s |

## Suite `features` — validated up to: behavior

Every case is counted once, at its earliest failing stage. crash, timeout and incomplete are subsets of the FAIL columns.

| version | cases | PASS | FAIL@load | FAIL@disassemble | FAIL@decompile | FAIL@syntax | FAIL@behavior | crash | timeout | incomplete | N/A | MISSING | HARNESS_ERROR |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3.10 | 219 | 15 | 0 | 0 | 126 | 15 | 36 | 6 | 0 | 93 | 27 | 0 | 0 |
| 3.11 | 219 | 15 | 0 | 0 | 165 | 6 | 15 | 3 | 0 | 124 | 18 | 0 | 0 |
| 3.12 | 219 | 9 | 0 | 0 | 175 | 11 | 12 | 0 | 0 | 142 | 12 | 0 | 0 |
| 3.13 | 219 | 0 | 0 | 0 | 210 | 0 | 0 | 0 | 0 | 210 | 9 | 0 | 0 |
| 3.14 | 219 | 0 | 219 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| all | 1095 | 39 | 219 | 0 | 676 | 32 | 63 | 9 | 0 | 569 | 66 | 0 | 0 |

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
| compile | 18.2 / 0.079 | 18.2 / 0.078 | 21.6 / 0.123 | 23.4 / 0.127 | 34.7 / 0.178 |
| load | 8.9 / 0.021 | 6.6 / 0.022 | 6.8 / 0.022 | 6.7 / 0.022 | 6.6 / 0.021 |
| disassemble | 4.0 / 0.022 | 4.1 / 0.022 | 4.6 / 0.022 | 4.4 / 0.022 | 4.6 / 0.022 |
| decompile | 3.9 / 0.021 | 4.3 / 0.022 | 4.3 / 0.022 | 4.3 / 0.022 | 4.5 / 0.021 |
| syntax | 10.9 / 0.075 | 12.4 / 0.075 | 12.9 / 0.075 | 14.9 / 0.075 | - |
| behavior | 12.9 / 0.129 | 14.2 / 0.130 | 11.3 / 0.129 | 35.0 / 0.181 | - |

### Most frequent failure causes per stage

**load** (219 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 219 | error | Bad MAGIC! | 3.14 |

**decompile** (676 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 204 | incomplete | Unsupported opcode: MAKE_FUNCTION (122) | 3.13 |
| 96 | incomplete | Unsupported opcode: MAKE_CELL (225) | 3.11, 3.12 |
| 51 | incomplete | Unsupported opcode: RETURN_GENERATOR (109) | 3.11, 3.12 |
| 35 | incomplete | Unsupported opcode: JUMP_IF_NOT_EXC_MATCH (210) | 3.10 |
| 24 | incomplete | Unsupported opcode: CALL_FUNCTION_EX (170) | 3.10, 3.11, 3.12 |
| 21 | diagnostic | Warning: Stack history is not empty! | 3.11, 3.12 |
| 21 | diagnostic | Something TERRIBLE happened! | 3.11, 3.12 |
| 18 | error | Unsupported argument found for LIST_EXTEND | 3.10, 3.11, 3.12 |
| 12 | incomplete | Warning: block stack is not empty! | 3.10, 3.11 |
| 12 | incomplete | Unsupported opcode: UNPACK_EX (189) | 3.10, 3.11, 3.12 |
| 9 | incomplete | Unsupported opcode: POP_JUMP_FORWARD_IF_NOT_NONE (221) | 3.11 |
| 9 | incomplete | Unsupported opcode: POP_JUMP_IF_NOT_NONE (238) | 3.12 |
| … | | 27 more distinct causes | |

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
| 3.14 | 270 | 0 | 165 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 105 | 0 | 0 |
| all | 1350 | 435 | 165 | 0 | 186 | 39 | 0 | 3 | 0 | 156 | 525 | 0 | 0 |

### PASS / applicable cases by optimization level

| opt | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
| --- | --- | --- | --- | --- | --- |
| -O0 | 45/55 | 38/55 | 40/55 | 22/55 | 0/55 |
| -O1 | 45/55 | 38/55 | 40/55 | 22/55 | 0/55 |
| -O2 | 45/55 | 38/55 | 40/55 | 22/55 | 0/55 |

### Stage wall time in seconds: total / median per case (cases where the stage ran)

behavior times the candidate run only; the reference run is not included.

| stage | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 |
| --- | --- | --- | --- | --- | --- |
| compile | 24.2 / 0.078 | 24.3 / 0.078 | 26.5 / 0.079 | 29.3 / 0.127 | 41.5 / 0.134 |
| load | 3.3 / 0.021 | 3.1 / 0.021 | 3.2 / 0.021 | 3.4 / 0.022 | 3.3 / 0.022 |
| disassemble | 3.3 / 0.021 | 3.3 / 0.021 | 3.5 / 0.022 | 3.3 / 0.022 | 3.3 / 0.021 |
| decompile | 3.2 / 0.021 | 3.3 / 0.021 | 3.3 / 0.021 | 3.3 / 0.021 | 3.3 / 0.021 |
| syntax | 10.7 / 0.074 | 10.5 / 0.075 | 10.7 / 0.074 | 11.6 / 0.075 | - |
| behavior | - | - | - | - | - |

### Most frequent failure causes per stage

**load** (165 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 165 | error | Bad MAGIC! | 3.14 |

**decompile** (186 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 78 | incomplete | Unsupported opcode: MAKE_FUNCTION (122) | 3.13 |
| 24 | incomplete | Unsupported opcode: RETURN_GENERATOR (109) | 3.11, 3.12 |
| 18 | incomplete | Unsupported opcode: MAKE_CELL (225) | 3.11, 3.12 |
| 12 | diagnostic | Warning: block stack is not empty! | 3.11 |
| 12 | diagnostic | Warning: Stack history is not empty! | 3.10, 3.12, 3.13 |
| 9 | incomplete | Unsupported opcode: JUMP_IF_NOT_EXC_MATCH (210) | 3.10 |
| 9 | incomplete | Warning: Stack history is not empty! | 3.10, 3.12 |
| 6 | incomplete | Unsupported opcode: POP_JUMP_BACKWARD_IF_TRUE (235) | 3.11 |
| 3 | incomplete | Unsupported use of GET_AITER outside of SETUP_LOOP | 3.10 |
| 3 | incomplete | Unsupported opcode: FORMAT_SIMPLE (120) | 3.13 |
| 3 | incomplete | Unsupported opcode: DICT_MERGE (213) | 3.10 |
| 3 | crash | killed by SIGSEGV | 3.11 |
| … | | 2 more distinct causes | |

**syntax** (39 cases)

| count | kind | cause | versions |
| --- | --- | --- | --- |
| 36 | syntax_error | SyntaxError: 'return' outside function | 3.10, 3.11, 3.12, 3.13 |
| 3 | syntax_error | SyntaxError: 'continue' not properly in loop | 3.12 |

