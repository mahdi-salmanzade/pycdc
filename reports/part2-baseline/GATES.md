# Gate dry runs against the frozen baseline

Generated with `harness/difftest.py gate --part N --results reports/part2-baseline/baseline.json --controls reports/part2-baseline/controls.json --upstream reports/part2-baseline/upstream_per_file_outcomes.json --limit 0`. These are expected to fail: they record the distance to each gate before any decompiler change.

## Part 4

```
gate for Part 4 (requirements of Parts 4..4)
  Part 4 (Make bytecode decoding trustworthy): 210/429 required cases reach disassemble
    ... 219 more
    manual evidence required: pycdas output matches normalized dis output of the same interpreter at the semantic level (opcodes, operands, names/constants, jump targets, exception table ranges, nested code objects) for every required fixture; the comparison tool is built in Part 4
    manual evidence required: hash-based .pyc headers (checked and unchecked) load for every required version
    manual evidence required: unsupported versions/formats fail with a clear message and nonzero exit; pycdas must not print '(Python -1.-1)' and exit 0
    manual evidence required: truncated or malformed .pyc inputs fail safely (no crash, no hang) under the harness sandbox
  vs baseline: regression 0
  vs baseline: missing_coverage 0
  vs baseline: harness_error 0
  controls: 1461 cases, 0 unexpected
  upstream token suite: 0 previously passing files no longer pass
GATE NOT PASSED (219 problems)
(exit 1)
```

## Part 5

```
gate for Part 5 (requirements of Parts 4..5)
  Part 4 (Make bytecode decoding trustworthy): 210/429 required cases reach disassemble
    ... 219 more
    manual evidence required: pycdas output matches normalized dis output of the same interpreter at the semantic level (opcodes, operands, names/constants, jump targets, exception table ranges, nested code objects) for every required fixture; the comparison tool is built in Part 4
    manual evidence required: hash-based .pyc headers (checked and unchecked) load for every required version
    manual evidence required: unsupported versions/formats fail with a clear message and nonzero exit; pycdas must not print '(Python -1.-1)' and exit 0
    manual evidence required: truncated or malformed .pyc inputs fail safely (no crash, no hang) under the harness sandbox
  Part 5 (Recover expressions, calls, functions, and classes): 0/162 required cases reach behavior
    ... 162 more
  vs baseline: regression 0
  vs baseline: missing_coverage 0
  vs baseline: harness_error 0
  controls: 1461 cases, 0 unexpected
  upstream token suite: 0 previously passing files no longer pass
GATE NOT PASSED (381 problems)
(exit 1)
```

## Part 6

```
gate for Part 6 (requirements of Parts 4..6)
  Part 4 (Make bytecode decoding trustworthy): 210/429 required cases reach disassemble
    ... 219 more
    manual evidence required: pycdas output matches normalized dis output of the same interpreter at the semantic level (opcodes, operands, names/constants, jump targets, exception table ranges, nested code objects) for every required fixture; the comparison tool is built in Part 4
    manual evidence required: hash-based .pyc headers (checked and unchecked) load for every required version
    manual evidence required: unsupported versions/formats fail with a clear message and nonzero exit; pycdas must not print '(Python -1.-1)' and exit 0
    manual evidence required: truncated or malformed .pyc inputs fail safely (no crash, no hang) under the harness sandbox
  Part 5 (Recover expressions, calls, functions, and classes): 0/162 required cases reach behavior
    ... 162 more
  Part 6 (Recover structured control flow and exceptions): 0/114 required cases reach behavior
    ... 114 more
  vs baseline: regression 0
  vs baseline: missing_coverage 0
  vs baseline: harness_error 0
  controls: 1461 cases, 0 unexpected
  upstream token suite: 0 previously passing files no longer pass
GATE NOT PASSED (495 problems)
(exit 1)
```

## Part 7

```
gate for Part 7 (requirements of Parts 4..7)
  Part 4 (Make bytecode decoding trustworthy): 210/429 required cases reach disassemble
    ... 219 more
    manual evidence required: pycdas output matches normalized dis output of the same interpreter at the semantic level (opcodes, operands, names/constants, jump targets, exception table ranges, nested code objects) for every required fixture; the comparison tool is built in Part 4
    manual evidence required: hash-based .pyc headers (checked and unchecked) load for every required version
    manual evidence required: unsupported versions/formats fail with a clear message and nonzero exit; pycdas must not print '(Python -1.-1)' and exit 0
    manual evidence required: truncated or malformed .pyc inputs fail safely (no crash, no hang) under the harness sandbox
  Part 5 (Recover expressions, calls, functions, and classes): 0/162 required cases reach behavior
    ... 162 more
  Part 6 (Recover structured control flow and exceptions): 0/114 required cases reach behavior
    ... 114 more
  Part 7 (Cover modern language features and interactions): 0/153 required cases reach behavior
    ... 153 more
  vs baseline: regression 0
  vs baseline: missing_coverage 0
  vs baseline: harness_error 0
  controls: 1461 cases, 0 unexpected
  upstream token suite: 0 previously passing files no longer pass
GATE NOT PASSED (648 problems)
(exit 1)
```
