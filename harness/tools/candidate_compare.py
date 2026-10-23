#!/usr/bin/env python3
"""Compare candidate decompiler builds against a frozen baseline.

Every candidate must have been run with the same harness, suites, interpreters
and -O levels as the baseline.  For each candidate this reports, per suite and
version, the outcome at the earliest failing stage, crashes, timeouts, silent
semantic mismatches (behavior differs although pycdc exited 0 with no marker
or diagnostic) and silent invalid output (no marker or diagnostic, but the
output does not compile).  It then reports what changed relative to the
baseline (fixed, regressed, failures moved to an earlier stage, new or
resolved crashes and silent failures) and which fixed cases the candidates
share.

usage: candidate_compare.py --baseline BASE.json NAME=RESULTS.json ... \
           [--json OUT.json] > COMPARISON.md
"""

import argparse
import collections
import itertools
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from difftest import STAGES, STAGE_RANK, case_key, load_results, version_tuple  # noqa: E402

COUNTS = ('applicable', 'PASS') + STAGES + ('crash', 'timeout', 'incomplete', 'diagnostic',
                                            'silent_mismatch', 'recovered_hang',
                                            'silent_invalid')


def silent(c):
    """'mismatch', 'invalid' or None for a case that failed without any signal."""
    if c['outcome'] != 'FAIL' or c['stages'].get('decompile', {}).get('status') != 'ok':
        return None
    if c['stage'] == 'behavior':
        return 'mismatch'
    if c['stage'] == 'syntax':
        return 'invalid'
    return None


def crashed(c):
    """A tool (load probe, pycdas, pycdc) crashed or timed out.  A timeout at the
    behavior stage is the recovered program hanging: a silent mismatch."""
    return c['outcome'] == 'FAIL' and c.get('kind') in ('crash', 'timeout') and \
        c['stage'] != 'behavior'


def tally(cases):
    t = collections.Counter()
    for c in cases:
        if c['outcome'] == 'N/A':
            continue
        t['applicable'] += 1
        if c['outcome'] == 'PASS':
            t['PASS'] += 1
            continue
        if c['outcome'] != 'FAIL':
            t[c['outcome']] += 1
            continue
        t[c['stage']] += 1
        if crashed(c) or c.get('kind') in ('incomplete', 'diagnostic'):
            t[c['kind']] += 1
        s = silent(c)
        if s:
            t['silent_' + s] += 1
        if s == 'mismatch' and c.get('kind') == 'timeout':
            t['recovered_hang'] += 1
    return t


def label(key):
    return '%s %s -O%d' % (key[1], '.'.join(map(str, key[2])), key[3])


def describe(c):
    if c['outcome'] != 'FAIL':
        return c['outcome']
    s = silent(c)
    return '%s@%s/%s%s' % ('FAIL', c['stage'], c.get('kind'), ' (silent)' if s else '')


def delta(base, cand):
    """Changes from base to cand, keyed by category; values are case keys."""
    d = collections.OrderedDict((k, []) for k in (
        'fixed', 'regressed', 'earlier_stage', 'later_stage', 'new_tool_crash',
        'resolved_tool_crash',
        'new_silent_mismatch', 'resolved_silent_mismatch', 'new_silent_invalid',
        'resolved_silent_invalid', 'missing', 'harness_error'))
    for key in sorted(set(base) | set(cand)):
        b, n = base.get(key), cand.get(key)
        if b is None or n is None:
            d['missing'].append(key)
            continue
        if n['outcome'] in ('MISSING', 'HARNESS_ERROR'):
            d['missing' if n['outcome'] == 'MISSING' else 'harness_error'].append(key)
            continue
        if b['outcome'] == 'N/A':
            continue
        if b['outcome'] != 'PASS' and n['outcome'] == 'PASS':
            d['fixed'].append(key)
        elif b['outcome'] == 'PASS' and n['outcome'] != 'PASS':
            d['regressed'].append(key)
        elif b['outcome'] == 'FAIL' and n['outcome'] == 'FAIL':
            rb, rn = STAGE_RANK[b['stage']], STAGE_RANK[n['stage']]
            if rn < rb:
                d['earlier_stage'].append(key)
            elif rn > rb:
                d['later_stage'].append(key)
        if crashed(n) and not crashed(b):
            d['new_tool_crash'].append(key)
        if crashed(b) and not crashed(n):
            d['resolved_tool_crash'].append(key)
        for kind in ('mismatch', 'invalid'):
            if silent(n) == kind and silent(b) != kind:
                d['new_silent_' + kind].append(key)
            if silent(b) == kind and silent(n) != kind:
                d['resolved_silent_' + kind].append(key)
    return d


def cell(s, n=160):
    s = str(s).replace('|', '\\|').replace('\n', ' ')
    return s if len(s) <= n else s[:n] + '…'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--baseline', required=True)
    ap.add_argument('candidates', nargs='+', metavar='NAME=RESULTS.json')
    ap.add_argument('--json', help='also write the counts and deltas as JSON')
    ap.add_argument('--limit', type=int, default=60, help='max listed cases per category')
    args = ap.parse_args()

    runs = collections.OrderedDict([('baseline', load_results(args.baseline))])
    for spec in args.candidates:
        name, path = spec.split('=', 1)
        runs[name] = load_results(path)
    idx = {name: {case_key(c): c for c in r['cases']} for name, r in runs.items()}
    names = list(runs)
    cands = names[1:]
    suites = sorted({c['suite'] for c in runs['baseline']['cases']})
    versions = sorted({c['version'] for c in runs['baseline']['cases']}, key=version_tuple)

    out = ['# Candidate comparison', '',
           'Generated by `harness/tools/candidate_compare.py`. Each case is counted once, at '
           'its earliest failing stage. *Silent mismatch*: pycdc exited 0 with no incomplete '
           'marker or diagnostic and the output compiled, but behavior differs; '
           '*recovered_hang* counts the silent mismatches where the recovered program did '
           'not finish. *Silent invalid*: no marker or diagnostic, but the output does not '
           'compile. *crash*/*timeout* count only the tools (load probe, pycdas, pycdc).', '',
           '| run | decompiler source | harness | created |', '| --- | --- | --- | --- |']
    for name, r in runs.items():
        p = r['meta']['provenance']
        out.append('| %s | `%s` %s | `%s`%s | %s |' % (
            name, (p.get('source_head') or '?')[:12],
            '(dirty)' if p.get('decompiler_source_dirty') else '',
            (p.get('harness_head') or '?')[:12], ' (dirty)' if p.get('harness_dirty') else '',
            r['meta']['created_utc']))
    out.append('')

    report = {'runs': {}, 'deltas': {}, 'overlap': {}}
    for suite in suites:
        out += ['## Suite `%s`' % suite, '']
        hdr = ['run', 'version'] + list(COUNTS)
        out += ['| ' + ' | '.join(hdr) + ' |', '|' + ' --- |' * len(hdr)]
        for name in names:
            for v in versions:
                cs = [c for k, c in idx[name].items() if k[0] == suite and c['version'] == v]
                t = tally(cs)
                report['runs'].setdefault(name, {}).setdefault(suite, {})[v] = dict(t)
                out.append('| %s | %s | %s |' % (name, v, ' | '.join(str(t.get(k, 0))
                                                                      for k in COUNTS)))
        out.append('')

        for name in cands:
            base = {k: c for k, c in idx['baseline'].items() if k[0] == suite}
            cand = {k: c for k, c in idx[name].items() if k[0] == suite}
            d = delta(base, cand)
            report['deltas'].setdefault(name, {})[suite] = {k: [label(x) for x in v]
                                                            for k, v in d.items()}
            out += ['### %s vs baseline (`%s`)' % (name, suite), '',
                    '| change | cases | by version |', '| --- | --- | --- |']
            for k, keys in d.items():
                byv = collections.Counter(c['version'] for c in (base.get(x) or cand[x]
                                                                  for x in keys))
                out.append('| %s | %d | %s |' % (k, len(keys), ', '.join(
                    '%s: %d' % (v, byv[v]) for v in versions if byv[v])))
            out.append('')
            for k in ('regressed', 'earlier_stage', 'new_tool_crash', 'new_silent_mismatch',
                      'new_silent_invalid'):
                if not d[k]:
                    continue
                out += ['**%s** (%d):' % (k, len(d[k])), '']
                for key in d[k][:args.limit]:
                    b, n = base[key], cand[key]
                    detail = n.get('cause') or ''
                    if silent(n) == 'mismatch':
                        detail = n['stages']['behavior'].get('first_difference', detail)
                    out.append('- `%s`: %s → %s: %s' % (label(key), describe(b), describe(n),
                                                       cell(detail)))
                if len(d[k]) > args.limit:
                    out.append('- … %d more' % (len(d[k]) - args.limit))
                out.append('')

        if len(cands) > 1:
            out += ['### Overlap of fixed cases (`%s`)' % suite, '',
                    '| pair | fixed by both | only first | only second |',
                    '| --- | --- | --- | --- |']
            for a, b in itertools.combinations(cands, 2):
                fa = set(report['deltas'][a][suite]['fixed'])
                fb = set(report['deltas'][b][suite]['fixed'])
                report['overlap']['%s/%s/%s' % (suite, a, b)] = {
                    'both': len(fa & fb), 'only_' + a: sorted(fa - fb),
                    'only_' + b: sorted(fb - fa)}
                out.append('| %s / %s | %d | %d | %d |' % (a, b, len(fa & fb), len(fa - fb),
                                                           len(fb - fa)))
            out.append('')

    out += _fixture_matrix(idx, names, versions)
    sys.stdout.write('\n'.join(out) + '\n')
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(report, f, indent=1, sort_keys=True)
            f.write('\n')


def _fixture_matrix(idx, names, versions):
    """Features fixtures whose pass count changed in any candidate."""
    passes = collections.defaultdict(lambda: collections.Counter())
    appl = collections.defaultdict(lambda: collections.Counter())
    for name in names:
        for key, c in idx[name].items():
            if key[0] != 'features':
                continue
            if c['outcome'] != 'N/A':
                appl[(c['fixture'], c['version'])][name] += 1
            if c['outcome'] == 'PASS':
                passes[(c['fixture'], c['version'])][name] += 1
    fixtures = sorted({k[0] for k in appl})
    out = ['## Feature fixtures with any change (PASS / applicable -O levels)', '',
           '| fixture | ' + ' | '.join(versions) + ' |', '|' + ' --- |' * (len(versions) + 1)]
    for fx in fixtures:
        row, changed = [], False
        for v in versions:
            a = appl[(fx, v)]
            if not a['baseline']:
                row.append('n/a')
                continue
            vals = [passes[(fx, v)][n] for n in names]
            changed |= len(set(vals)) > 1
            row.append(' / '.join(str(x) for x in vals))
        if changed:
            out.append('| `%s` | %s |' % (fx, ' | '.join(row)))
    out += ['', 'Cells list ' + ' / '.join(names) + '.', '']
    return out


if __name__ == '__main__':
    main()
