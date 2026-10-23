#!/usr/bin/env python3
"""Run upstream's token-level regression suite against one build, sandboxed.

Runs reports/part1-baseline/per_file_outcomes.py (the per-file wrapper around
tests/run_tests.py) with the build directory as its working directory, under
the same isolation as the differential harness (harness/sandbox.py): scrubbed
environment, no network, writes only inside the build directory, resource
limits.  Use it for any binary that was not built from reviewed source, such
as an upstream pull request under evaluation.

The fixtures and expectations always come from this repository's tests/, so
every build is measured against the same frozen corpus.  token_dump runs under
the pinned interpreter given by --python (default: the pinned 3.12).

usage: upstream_suite.py --build-dir DIR --json OUT.json [--python X.Y]
"""

import argparse
import os
import shutil
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
HARNESS = os.path.dirname(HERE)
REPO = os.path.dirname(HARNESS)
sys.path.insert(0, HARNESS)
import sandbox  # noqa: E402
from difftest import load_config, resolve_interpreters  # noqa: E402

RUNNER = os.path.join(REPO, 'reports', 'part1-baseline', 'per_file_outcomes.py')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--build-dir', required=True, help='directory containing ./pycdc')
    ap.add_argument('--json', required=True, help='per-file outcomes output path')
    ap.add_argument('--python', default='3.12', help='pinned interpreter for token_dump')
    ap.add_argument('--timeout', type=int, default=900)
    args = ap.parse_args()

    build = os.path.realpath(args.build_dir)
    if not os.path.exists(os.path.join(build, 'pycdc')):
        sys.exit('no pycdc in %s' % build)
    mode = sandbox.default_mode()
    if mode is None:
        sys.exit('no sandbox available on this platform')
    entry = resolve_interpreters(None, {}, [args.python])[args.python]
    if entry['status'] != 'ok':
        sys.exit('interpreter %s: %s' % (args.python, entry.get('reason')))
    python = entry['path']
    read_allow = {REPO, build, os.path.expanduser(load_config()['install_dir']),
                  os.path.dirname(os.path.dirname(os.path.realpath(python)))}
    r = sandbox.run([python, '-I', RUNNER, '--json', 'upstream_per_file_outcomes.json'],
                    build, mode, args.timeout, read_allow, tag='upstream-suite')
    sys.stdout.write(r.stdout.decode('utf-8', 'replace'))
    sys.stderr.write(r.stderr.decode('utf-8', 'replace'))
    if r.timed_out or r.returncode is None or r.returncode < 0:
        sys.exit('upstream suite did not finish (timed_out=%s, rc=%s)' % (r.timed_out,
                                                                         r.returncode))
    os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
    shutil.copyfile(os.path.join(build, 'upstream_per_file_outcomes.json'), args.json)
    return r.returncode


if __name__ == '__main__':
    sys.exit(main())
