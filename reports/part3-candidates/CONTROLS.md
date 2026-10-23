# Harness control results

| | |
| --- | --- |
| created (UTC) | 2026-10-23T01:41:59Z |
| command | `harness/difftest.py controls --workroot build/part3/work-controls --out reports/part3-candidates/controls.json --summary reports/part3-candidates/CONTROLS.md` |
| host | macOS-26.7.1-arm64-arm-64bit, harness Python 3.12.2 |
| sandbox | macos-sandbox-exec |
| optimization levels | 0, 1, 2 |
| decompiler source | `27ef3c6700df5a356bfc356ee6ff178413a12301` (bootstrap), dirty files: none |
| harness | `27ef3c6700df5a356bfc356ee6ff178413a12301`, dirty files: 0 |
| CPython 3.10 | 3.10.22, magic 3439, ok |
| CPython 3.11 | 3.11.17, magic 3495, ok |
| CPython 3.12 | 3.12.15, magic 3531, ok |
| CPython 3.13 | 3.13.17, magic 3571, ok |
| CPython 3.14 | 3.14.9, magic 3627, ok |
| wall time | 38.6s |

## Positive controls (original source as candidate; must match)

1029 cases: OK=1029


## Negative controls (deliberate semantic changes; must be detected)

| control | fixture | declared channel | expected | outcome counts | channels seen |
| --- | --- | --- | --- | --- | --- |
| aliasing | expressions/assignment_unpacking | observe.outcome | detect | DETECTED=15 | observe.outcome |
| assert_condition | exceptions/assert_statements | observe.outcome | dead, detect | DETECTED=5, OK_NOT_EXPECTED=10 | observe.outcome |
| async_order | async/async_for_with | observe.transcript | detect | DETECTED=15 | observe.transcript |
| atexit_stderr | functions/exit_handlers | process.stderr | detect | DETECTED=15 | process.stderr |
| atexit_stdout | functions/exit_handlers | process.stdout | detect | DETECTED=15 | process.stdout |
| branch_condition | loops/while_loops | observe.outcome | detect | DETECTED=15 | observe.outcome |
| closure_binding | closures/closure_basics | observe.outcome | detect | DETECTED=15 | observe.outcome |
| default_value | exceptions/with_statements | globals.outcome | detect | DETECTED=15 | globals.outcome |
| docstring_text | functions/docstrings | observe.outcome | dead, detect | DETECTED=10, OK_NOT_EXPECTED=5 | globals.outcome, observe.outcome |
| dropped_statement | expressions/delete_statements | observe.transcript | detect | DETECTED=15 | observe.transcript |
| enter_exit_order | exceptions/with_statements | observe.transcript | detect | DETECTED=15 | observe.transcript |
| evaluation_count | branches/short_circuit | observe.transcript | detect | DETECTED=15 | observe.transcript |
| except_star_split | version_specific/except_star | observe.outcome | detect | DETECTED=12 | observe.outcome, observe.transcript |
| exception_cause_dropped | exceptions/raise_and_chaining | observe.outcome | detect | DETECTED=15 | observe.outcome |
| exception_message | exceptions/raise_and_chaining | observe.outcome | detect | DETECTED=15 | observe.outcome |
| exception_swallowed | exceptions/raise_and_chaining | observe.transcript | detect | DETECTED=15 | observe.transcript |
| exception_type | exceptions/raise_and_chaining | observe.outcome | detect | DETECTED=15 | observe.outcome |
| finalize_text | generators/generator_cleanup | finalize.transcript | detect | DETECTED=15 | finalize.transcript |
| iteration_extra_item | generators/generator_protocol | observe.outcome | detect | DETECTED=15 | observe.outcome |
| match_alternative | branches/match_literals_captures | observe.outcome | detect | DETECTED=15 | observe.outcome |
| module_global | functions/defaults | globals.outcome | detect | DETECTED=15 | globals.outcome |
| module_stdout | classes/metaclasses | module.transcript | detect | DETECTED=15 | module.transcript |
| mutation_order | functions/defaults | observe.outcome | detect | DETECTED=15 | observe.outcome |
| positional_only | calls/arguments | observe.outcome | detect | DETECTED=15 | globals.outcome, observe.outcome |
| return_value | expressions/arithmetic | observe.outcome | detect | DETECTED=15 | observe.outcome |
| side_effect_order | calls/evaluation_order | observe.transcript | detect | DETECTED=15 | observe.transcript |
| stderr_to_stdout | exceptions/try_except | observe.transcript | detect | DETECTED=15 | observe.transcript |
| stdout_text | loops/iteration_protocol | observe.transcript | detect | DETECTED=15 | observe.transcript |
| truth_test_count | branches/truthiness | observe.transcript | detect | DETECTED=15 | observe.outcome, observe.transcript |

Unexpected negative-control outcomes: 0
