#!/usr/bin/env python3
"""Write the test inputs of upstream PR #617 to one .py file per case.

PR #617 keeps its cases as string literals in tests/modern_roundtrip.py: the
CASES dict, plus one case added inside main() for 3.13.  This script only
parses that file and evaluates string literals (ast.literal_eval).  It never
imports or runs the PR's code, and the extracted cases are only compiled and
decompiled by the harness, never executed (D-012).

usage: extract_pr617_cases.py PATH/TO/modern_roundtrip.py OUTDIR
"""

import ast
import os
import sys


def main():
    src, outdir = sys.argv[1], sys.argv[2]
    with open(src, encoding='utf-8') as f:
        tree = ast.parse(f.read())
    cases = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == 'CASES' for t in node.targets):
            cases.update(ast.literal_eval(node.value))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Subscript) \
                and isinstance(node.targets[0].value, ast.Name) \
                and node.targets[0].value.id == 'cases':
            cases[ast.literal_eval(node.targets[0].slice)] = ast.literal_eval(node.value)
    os.makedirs(outdir, exist_ok=True)
    for name, text in sorted(cases.items()):
        with open(os.path.join(outdir, name + '.py'), 'w', encoding='utf-8') as f:
            f.write(text)
    print('%d cases: %s' % (len(cases), ', '.join(sorted(cases))))


if __name__ == '__main__':
    main()
