#!/usr/bin/env python3
"""Per-file outcome report for upstream's existing regression suite.

Read-only wrapper around tests/run_tests.py.  It reuses run_tests.decompyle_one()
so the pass criterion is byte-for-byte the upstream one (pycdc must exit 0 with
no diagnostic output, and the token_dump of its output must equal
tests/tokenized/<name>.txt), but reports every .pyc separately:

  tests/compiled/*.pyc  -> PASS or FAIL
  tests/xfail/*.pyc     -> XFAIL or XPASS

The upstream runner reports per test name only, leaves the XFAIL count blank,
and never prints XPASS.  This script does not change that runner or any
fixture.  Like the upstream runner it has no per-file timeout.

Usage (from a build directory containing ./pycdc):
    cd build/debug
    python3.12 ../../reports/part1-baseline/per_file_outcomes.py --json out.json

token_dump runs under the interpreter executing this script (sys.executable),
exactly as in run_tests.py, so record which interpreter was used.
"""

import argparse
import glob
import json
import os
import platform
import sys
import tempfile
from collections import Counter

REPO = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..'))
TEST_DIR = os.path.join(REPO, 'tests')
sys.path.insert(0, TEST_DIR)
import run_tests  # noqa: E402


def fixture_version(pyc_name):
    # <test_name>.<major>.<minor>.pyc, where test_name may itself contain dots
    parts = pyc_name[:-len('.pyc')].split('.')
    return '.'.join(parts[-2:])


def stage_of_failure(out_base):
    if os.path.exists(out_base + '.err'):
        return 'pycdc'          # nonzero exit or any stdout/stderr output
    if os.path.exists(out_base + '.tok.err'):
        return 'token_dump'     # recovered source failed to tokenize
    if os.path.exists(out_base + '.tok.diff'):
        return 'token_mismatch'
    return 'unknown'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', help='write per-file results to this path')
    args = ap.parse_args()

    if not os.path.exists(os.path.join(os.getcwd(), 'pycdc')):
        sys.exit('run from a build directory containing ./pycdc')

    expectations = {os.path.splitext(os.path.basename(p))[0]: p
                    for p in glob.glob(os.path.join(TEST_DIR, 'tokenized', '*.txt'))}
    results = []
    unmatched = []
    seen = set()
    outdir = tempfile.mkdtemp(prefix='pycdc-part1-')

    for test_name in sorted(expectations):
        with open(expectations[test_name], 'r', encoding='utf-8', errors='replace') as f:
            expect = f.read()
        for subset in ('compiled', 'xfail'):
            pattern = os.path.join(TEST_DIR, subset, test_name + '.?.*.pyc')
            for pyc in sorted(glob.glob(pattern)):
                seen.add(pyc)
                ok, _ = run_tests.decompyle_one(test_name, pyc, outdir, expect)
                name = os.path.basename(pyc)
                if subset == 'compiled':
                    outcome = 'PASS' if ok else 'FAIL'
                else:
                    outcome = 'XPASS' if ok else 'XFAIL'
                stage = None if ok else stage_of_failure(os.path.join(outdir, name))
                results.append({'file': '{}/{}'.format(subset, name), 'test': test_name,
                                'version': fixture_version(name), 'outcome': outcome,
                                'failed_stage': stage})

    for subset in ('compiled', 'xfail'):
        for pyc in sorted(glob.glob(os.path.join(TEST_DIR, subset, '*.pyc'))):
            if pyc not in seen:
                unmatched.append('{}/{}'.format(subset, os.path.basename(pyc)))
    no_fixture = sorted(t for t in expectations
                        if not any(r['test'] == t for r in results))

    totals = Counter(r['outcome'] for r in results)
    stages = Counter((r['outcome'], r['failed_stage']) for r in results if r['failed_stage'])
    by_version = {}
    for r in results:
        by_version.setdefault(r['version'], Counter())[r['outcome']] += 1

    def vkey(v):
        return tuple(int(x) for x in v.split('.'))

    print('interpreter for token_dump: {} {}'.format(platform.python_version(), sys.executable))
    print('totals: ' + ', '.join('{}={}'.format(k, totals.get(k, 0))
                                 for k in ('PASS', 'FAIL', 'XFAIL', 'XPASS')))
    for (outcome, stage), n in sorted(stages.items()):
        print('  {} at stage {}: {}'.format(outcome, stage, n))
    print('by fixture version:')
    for v in sorted(by_version, key=vkey):
        c = by_version[v]
        print('  {:>5}  '.format(v) + '  '.join('{}={}'.format(k, c[k])
                                               for k in ('PASS', 'FAIL', 'XFAIL', 'XPASS') if c[k]))
    for r in results:
        if r['outcome'] in ('FAIL', 'XPASS'):
            print('{}: {} ({})'.format(r['outcome'], r['file'], r['failed_stage']))
    print('.pyc never run (no tokenized expectation): {}'.format(unmatched or 'none'))
    print('expectations with no .pyc: {}'.format(no_fixture or 'none'))

    if args.json:
        with open(args.json, 'w') as f:
            json.dump({'interpreter': platform.python_version(),
                       'totals': dict(totals),
                       'results': results,
                       'unrun_pyc': unmatched,
                       'expectations_without_pyc': no_fixture}, f, indent=1, sort_keys=True)
            f.write('\n')


if __name__ == '__main__':
    main()
