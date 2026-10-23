#!/usr/bin/env python3
"""Differential test harness for pycdc.

Commands
  interpreters  resolve and verify the pinned interpreters
  run           compile fixtures with the pinned interpreters and run every
                validation stage against a pycdc build
  controls      validate the harness itself: positive controls (the original
                source as candidate must match) and negative controls
                (deliberately changed sources must be detected)
  compare       compare a results file with a frozen baseline
  gate          check a Part 4-7 completion gate against requirements.json
  list          print the fixture matrix
  summarize     render a results file as Markdown

Stages, in order (a case is classified at its earliest failing stage):
  load         .pyc header + marshal loading (harness/tools/load_probe.cpp
               linked against the build's own libpycxx.a)
  disassemble  pycdas exits 0, prints nothing to stderr, emits no
               <INVALID>/<N> opcodes
  decompile    pycdc exits 0, prints nothing to stderr, emits no
               "# WARNING: Decompyle incomplete" marker
  syntax       recovered source compiles under the same interpreter at the
               same optimization level
  behavior     recovered source observably behaves like the compiled .pyc
               (harness/workers/observe.py defines the observation contract)

See harness/README.md for the workflow and policies.
"""

import argparse
import collections
import concurrent.futures
import glob
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time

HARNESS = os.path.dirname(os.path.realpath(__file__))
REPO = os.path.dirname(HARNESS)
sys.path.insert(0, HARNESS)
import sandbox  # noqa: E402

WORKERS = os.path.join(HARNESS, 'workers')
STAGES = ('load', 'disassemble', 'decompile', 'syntax', 'behavior')
SUITES = {
    # Authored, reviewed fixtures with an observe() driver: validated to behavior.
    'features': {'root': os.path.join(HARNESS, 'fixtures'), 'pattern': '*/*.py',
                 'behavior': True},
    # Upstream's tests/input sources: compiled and decompiled, never executed.
    'upstream-inputs': {'root': os.path.join(REPO, 'tests', 'input'), 'pattern': '*.py',
                        'behavior': False},
}
TIMEOUTS = {'compile': 30, 'load': 10, 'disassemble': 30, 'decompile': 30,
            'syntax': 30, 'observe': 20}
PY_ENV = {'PYTHONHASHSEED': '0', 'PYTHONUTF8': '1', 'PYTHONDONTWRITEBYTECODE': '1',
          'PYTHONNOUSERSITE': '1'}
OPT_FLAGS = {0: [], 1: ['-O'], 2: ['-OO']}
INCOMPLETE_MARKER = '# WARNING: Decompyle incomplete'
INVALID_OPCODE = re.compile(r'<INVALID>|^\s*\d+\s+<-?\d+>', re.M)
HEADER = re.compile(r'^#\s*([a-z-]+):\s*(.*?)\s*$')
ADDR = re.compile(r' at 0x[0-9A-Fa-f]+')
LINENO = re.compile(r'line \d+')


# ---------------------------------------------------------------- utilities

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 16), b''):
            h.update(chunk)
    return h.hexdigest()


def git(root, *args):
    r = subprocess.run(['git', '-C', root] + list(args), capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None


def text(data):
    return data.decode('utf-8', 'replace')


def first_line(s):
    for line in s.splitlines():
        if line.strip():
            return line.strip()[:240]
    return ''


def read_header(path):
    meta = {}
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            if not line.startswith('#'):
                break
            m = HEADER.match(line)
            if m:
                meta.setdefault(m.group(1), m.group(2))
    return meta


def version_tuple(minor):
    return tuple(int(x) for x in minor.split('.'))


def applicable(requires, minor):
    """requires: comma-separated clauses such as '>=3.11' or '>=3.10,<3.14'."""
    if not requires:
        return True
    v = version_tuple(minor)
    ops = {'>=': lambda a, b: a >= b, '>': lambda a, b: a > b, '<=': lambda a, b: a <= b,
           '<': lambda a, b: a < b, '==': lambda a, b: a == b}
    for clause in requires.split(','):
        m = re.match(r'^\s*(>=|<=|==|>|<)\s*(\d+)\.(\d+)\s*$', clause)
        if not m:
            raise ValueError('bad requires clause: {!r}'.format(clause))
        if not ops[m.group(1)](v, (int(m.group(2)), int(m.group(3)))):
            return False
    return True


def parse_json_stdout(data):
    for line in reversed(text(data).splitlines()):
        line = line.strip()
        if line.startswith('{'):
            try:
                return json.loads(line)
            except ValueError:
                return None
    return None


def opt_list(s):
    return [int(x) for x in s.split(',') if x != '']


# ------------------------------------------------------------- interpreters

PROBE = ('import sys, importlib.util as u; '
         'print("%d.%d.%d" % sys.version_info[:3], '
         'int.from_bytes(u.MAGIC_NUMBER[:2], "little"))')


def load_config():
    with open(os.path.join(HARNESS, 'interpreters.json')) as f:
        return json.load(f)


def resolve_interpreters(install_dir=None, overrides=None, wanted=None):
    cfg = load_config()
    install_dir = os.path.expanduser(install_dir or cfg['install_dir'])
    overrides = overrides or {}
    out = collections.OrderedDict()
    for minor, spec in cfg['interpreters'].items():
        if wanted and minor not in wanted:
            continue
        entry = {'minor': minor, 'pinned': spec['version'], 'magic': spec['magic']}
        path = overrides.get(minor)
        if not path:
            hits = sorted(glob.glob(os.path.join(
                install_dir, 'cpython-%s-*' % spec['version'], 'bin', 'python' + minor)))
            path = hits[0] if hits else None
        entry['path'] = path
        if not path or not os.path.exists(path):
            entry.update(status='missing', reason='not installed under ' + install_dir)
        else:
            r = subprocess.run([path, '-I', '-c', PROBE], capture_output=True, text=True,
                               timeout=60)
            got = r.stdout.split()
            if r.returncode != 0 or len(got) != 2:
                entry.update(status='missing', reason='probe failed: ' + first_line(r.stderr))
            elif got[0] != spec['version'] or int(got[1]) != spec['magic']:
                entry.update(status='mismatch',
                             reason='found %s magic %s' % (got[0], got[1]))
            else:
                entry['status'] = 'ok'
        out[minor] = entry
    return out


# --------------------------------------------------------------- provenance

def provenance(source_root, binaries):
    dirty = git(source_root, 'status', '--porcelain', '--', '*.cpp', '*.h', '*.inl',
                'CMakeLists.txt', ':(exclude)harness')
    harness_dirty = git(REPO, 'status', '--porcelain', '--', 'harness')
    prov = {
        'source_root': os.path.relpath(source_root, REPO) if source_root.startswith(REPO)
        else source_root,
        'source_head': git(source_root, 'rev-parse', 'HEAD'),
        'source_branch': git(source_root, 'rev-parse', '--abbrev-ref', 'HEAD'),
        'decompiler_source_dirty': dirty.splitlines() if dirty else [],
        'harness_head': git(REPO, 'rev-parse', 'HEAD'),
        'harness_dirty': harness_dirty.splitlines() if harness_dirty else [],
        'binaries': {},
    }
    for name, path in binaries.items():
        prov['binaries'][name] = {'path': path, 'sha256': sha256_file(path)}
    return prov


def build_load_probe(source_root, build_dir, workroot):
    lib = os.path.join(build_dir, 'libpycxx.a')
    out = os.path.join(workroot, 'load_probe')
    cmd = [os.environ.get('CXX', 'c++'), '-std=c++11', '-O1', '-I' + source_root,
           os.path.join(HARNESS, 'tools', 'load_probe.cpp'), lib, '-o', out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit('failed to build load probe:\n' + r.stderr)
    return out


# ------------------------------------------------------------------ stages

def stage(status, kind=None, cause=None, seconds=None, **extra):
    d = {'status': status}
    if kind:
        d['kind'] = kind
    if cause:
        d['cause'] = cause
    if seconds is not None:
        d['seconds'] = round(seconds, 3)
    d.update(extra)
    return d


def proc_failure(r):
    if r.timed_out:
        return 'timeout', 'exceeded %ss limit' % round(r.seconds, 1)
    if r.signal:
        if r.signal_name() == 'SIGXFSZ':
            return 'crash', 'output size limit (SIGXFSZ)'
        return 'crash', 'killed by %s' % r.signal_name()
    return None


def clean_cause(s, wd):
    line = first_line(s).replace(wd + os.sep, '').replace(wd, '<wd>')
    m = re.match(r'^Error (?:decompyling|disassembling|loading file) \S+: (.*)$', line)
    return m.group(1) if m else line


def run_py(job, wd, argv, tag, timeout, opt=None):
    opt = job['opt'] if opt is None else opt
    full = [job['python']] + OPT_FLAGS[opt] + ['-s', '-B'] + argv
    return sandbox.run(full, wd, job['sandbox'], timeout, read_allow=job['read_allow'],
                       env_extra=PY_ENV, tag=tag)


def run_bin(job, wd, argv, tag, timeout):
    return sandbox.run(argv, wd, job['sandbox'], timeout, read_allow=job['read_allow'],
                       tag=tag)


def do_compile(job, wd):
    shutil.copyfile(job['path'], os.path.join(wd, 'fixture.py'))
    r = run_py(job, wd, [os.path.join(WORKERS, 'compile_fixture.py'), 'fixture.py',
                         'fixture.pyc', str(job['opt']), 'fixture.py'],
               'compile', TIMEOUTS['compile'])
    info = parse_json_stdout(r.stdout)
    f = proc_failure(r)
    if f:
        return stage('fail', f[0], f[1], r.seconds)
    if not info:
        return stage('fail', 'error', clean_cause(text(r.stderr), wd) or 'no result', r.seconds)
    if not info.get('ok'):
        return stage('fail', 'compile_error',
                     '%s: %s' % (info.get('error'), info.get('message')), r.seconds)
    if info['magic'] != job['magic']:
        return stage('fail', 'error', 'magic %s != pinned %s' % (info['magic'], job['magic']),
                     r.seconds)
    return stage('ok', seconds=r.seconds)


def do_load(job, wd):
    r = run_bin(job, wd, [job['load_probe'], 'fixture.pyc'], 'load', TIMEOUTS['load'])
    f = proc_failure(r)
    if f:
        return stage('fail', f[0], f[1], r.seconds)
    out, err = text(r.stdout).strip(), text(r.stderr).strip()
    if r.returncode != 0 or err:
        return stage('fail', 'error', clean_cause(err, wd) or 'exit %d' % r.returncode,
                     r.seconds)
    if out != 'ok ' + job['minor']:
        return stage('fail', 'error', 'loaded as %r, expected %s' % (out, job['minor']),
                     r.seconds)
    return stage('ok', seconds=r.seconds)


def do_disassemble(job, wd):
    r = run_bin(job, wd, [job['pycdas'], 'fixture.pyc'], 'pycdas', TIMEOUTS['disassemble'])
    f = proc_failure(r)
    if f:
        return stage('fail', f[0], f[1], r.seconds)
    out, err = text(r.stdout), text(r.stderr)
    if r.returncode != 0:
        return stage('fail', 'error', clean_cause(err, wd) or 'exit %d' % r.returncode,
                     r.seconds)
    m = INVALID_OPCODE.search(out)
    if m:
        line = out[out.rfind('\n', 0, m.start()) + 1:].split('\n', 1)[0]
        return stage('fail', 'invalid_opcode', ' '.join(line.split())[:200], r.seconds)
    if err.strip():
        return stage('fail', 'diagnostic', clean_cause(err, wd), r.seconds)
    return stage('ok', seconds=r.seconds)


def do_decompile(job, wd):
    """Returns (stage, output_usable)."""
    r = run_bin(job, wd, [job['pycdc'], 'fixture.pyc'], 'pycdc', TIMEOUTS['decompile'])
    with open(os.path.join(wd, 'recovered.py'), 'wb') as f:
        f.write(r.stdout)
    f = proc_failure(r)
    if f:
        return stage('fail', f[0], f[1], r.seconds), False
    out, err = text(r.stdout), text(r.stderr)
    if r.returncode != 0:
        return stage('fail', 'error', clean_cause(err, wd) or 'exit %d' % r.returncode,
                     r.seconds), False
    if INCOMPLETE_MARKER in out:
        return stage('fail', 'incomplete', clean_cause(err, wd) or 'incomplete marker',
                     r.seconds), True
    if err.strip():
        return stage('fail', 'diagnostic', clean_cause(err, wd), r.seconds), True
    return stage('ok', seconds=r.seconds), True


def do_syntax(job, wd, source):
    r = run_py(job, wd, [os.path.join(WORKERS, 'syntax_check.py'), source, str(job['opt'])],
               'syntax', TIMEOUTS['syntax'])
    f = proc_failure(r)
    if f:
        return stage('fail', f[0], f[1], r.seconds)
    info = parse_json_stdout(r.stdout)
    if not info:
        return stage('fail', 'error', clean_cause(text(r.stderr), wd) or 'no result', r.seconds)
    if not info['ok']:
        return stage('fail', 'syntax_error', '%s: %s' % (info['error'], info['message']),
                     r.seconds, lineno=info.get('lineno'), text=info.get('text'))
    extra = {'warnings': info['warnings']} if info.get('warnings') else {}
    return stage('ok', seconds=r.seconds, **extra)


def observe(job, wd, mode_args, tag):
    out = os.path.join(wd, tag + '.json')
    if os.path.exists(out):
        os.unlink(out)
    r = run_py(job, wd, [os.path.join(WORKERS, 'observe.py')] + mode_args + ['--out', out],
               tag, TIMEOUTS['observe'])
    data = None
    if os.path.exists(out):
        with open(out, encoding='utf-8') as f:
            try:
                data = json.load(f)
            except ValueError:
                data = None
    return r, data


def channels(obs, proc):
    ch = collections.OrderedDict()
    ch['env'] = obs['env']
    for part in ('module', 'globals', 'observe', 'finalize'):
        o = obs.get(part)
        if o is None:
            ch[part + '.present'] = False
            continue
        ch[part + '.transcript'] = o['transcript']
        ch[part + '.outcome'] = {k: v for k, v in o.items() if k != 'transcript'}
    ch['process.stdout'] = ADDR.sub(' at 0x?', text(proc.stdout))
    ch['process.stderr'] = LINENO.sub('line ?', ADDR.sub(' at 0x?', text(proc.stderr)))
    return ch


def first_difference(a, b, path=''):
    if type(a) is not type(b):
        return path, a, b
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if a.get(k) != b.get(k):
                return first_difference(a.get(k), b.get(k), path + '.' + str(k))
        return None
    if isinstance(a, list):
        for i, (x, y) in enumerate(zip(a, b)):
            if x != y:
                return first_difference(x, y, '%s[%d]' % (path, i))
        if len(a) != len(b):
            return '%s(len)' % path, len(a), len(b)
        return None
    return (path, a, b) if a != b else None


def short(v, n=160):
    s = json.dumps(v, sort_keys=True) if not isinstance(v, str) else repr(v)
    return s if len(s) <= n else s[:n] + '...'


def compare_obs(ref, ref_proc, cand, cand_proc):
    a, b = channels(ref, ref_proc), channels(cand, cand_proc)
    diff = [k for k in list(a) + [k for k in b if k not in a] if a.get(k) != b.get(k)]
    if not diff:
        return [], None
    fd = first_difference(a.get(diff[0]), b.get(diff[0]), diff[0])
    detail = None
    if fd:
        detail = '%s: reference %s, candidate %s' % (fd[0], short(fd[1]), short(fd[2]))
    return diff, detail


def reference(job, wd):
    """Observe the compiled .pyc; returns (proc, observation, error)."""
    r, data = observe(job, wd, ['--pyc', 'fixture.pyc'], 'reference')
    f = proc_failure(r)
    if f:
        return r, None, 'reference %s: %s' % f
    if data is None:
        return r, None, 'reference produced no observation: ' + first_line(text(r.stderr))
    return r, data, None


def do_behavior(job, wd, ref, source):
    ref_proc, ref_obs = ref
    r, cand = observe(job, wd, ['--source', source, '--optimize', str(job['opt']),
                                '--filename', 'fixture.py'], 'candidate')
    f = proc_failure(r)
    if f:
        return stage('fail', f[0], 'candidate ' + f[1], r.seconds)
    if cand is None:
        return stage('fail', 'error', 'candidate produced no observation: '
                     + first_line(text(r.stderr)), r.seconds)
    diff, detail = compare_obs(ref_obs, ref_proc, cand, r)
    if 'env' in diff:
        return stage('harness_error', 'env', 'reference/candidate environments differ')
    if diff:
        return stage('fail', 'mismatch', ', '.join(diff), r.seconds, channels=diff,
                     first_difference=detail)
    return stage('ok', seconds=r.seconds)


# ------------------------------------------------------------------- cases

def case_key(c):
    return (c['suite'], c['fixture'], version_tuple(c['version']), c['opt'])


def new_case(job):
    return {'suite': job['suite'], 'fixture': job['id'], 'category': job['category'],
            'version': job['minor'], 'opt': job['opt']}


def classify(case, stages, policy_behavior):
    for name in STAGES:
        st = stages.get(name)
        if st and st['status'] == 'fail':
            case.update(outcome='FAIL', stage=name, kind=st.get('kind'), cause=st.get('cause'))
            return case
    case['outcome'] = 'PASS'
    case['validated_to'] = 'behavior' if policy_behavior else 'syntax'
    return case


def run_case(job):
    case = new_case(job)
    wd = job['workdir']
    shutil.rmtree(wd, ignore_errors=True)
    os.makedirs(wd)
    case['hashes'] = {'source': sha256_file(job['path'])}
    stages = collections.OrderedDict()
    case['stages'] = stages

    stages['compile'] = do_compile(job, wd)
    if stages['compile']['status'] != 'ok':
        if job['suite'] == 'features':
            case.update(outcome='HARNESS_ERROR', stage='compile',
                        cause=stages['compile'].get('cause'))
        else:
            case.update(outcome='N/A', cause='source does not compile on this interpreter: '
                        + str(stages['compile'].get('cause')))
        return case
    case['hashes']['pyc'] = sha256_file(os.path.join(wd, 'fixture.pyc'))

    ref = None
    if job['behavior']:
        ref_proc, ref_obs, err = reference(job, wd)
        if err:
            case.update(outcome='HARNESS_ERROR', stage='reference', cause=err)
            return case
        ref = (ref_proc, ref_obs)

    stages['load'] = do_load(job, wd)
    stages['disassemble'] = do_disassemble(job, wd)
    stages['decompile'], usable = do_decompile(job, wd)
    case['hashes']['recovered'] = sha256_file(os.path.join(wd, 'recovered.py'))
    if usable:
        stages['syntax'] = do_syntax(job, wd, 'recovered.py')
    else:
        stages['syntax'] = stage('not_run', cause='no usable decompiler output')
    if not job['behavior']:
        stages['behavior'] = stage('not_run', cause='suite policy: not executed')
    elif stages['syntax']['status'] != 'ok':
        stages['behavior'] = stage('not_run', cause='recovered source does not compile')
    else:
        stages['behavior'] = do_behavior(job, wd, ref, 'recovered.py')
        if stages['behavior']['status'] == 'harness_error':
            case.update(outcome='HARNESS_ERROR', stage='behavior',
                        cause=stages['behavior'].get('cause'))
            return case
    return classify(case, stages, job['behavior'])


def run_control_case(job):
    """Positive control: candidate is the fixture's own source (must match).
    Negative control: candidate is a deliberately changed source (must not)."""
    case = new_case(job)
    case.update(control=job.get('control'), channel=job.get('channel'),
                expect=job['expect'])
    wd = job['workdir']
    shutil.rmtree(wd, ignore_errors=True)
    os.makedirs(wd)
    st = do_compile(job, wd)
    if st['status'] != 'ok':
        case.update(outcome='HARNESS_ERROR', cause='fixture compile: %s' % st.get('cause'))
        return case
    ref_proc, ref_obs, err = reference(job, wd)
    if err:
        case.update(outcome='HARNESS_ERROR', cause=err)
        return case
    shutil.copyfile(job['candidate'], os.path.join(wd, 'candidate_src.py'))
    syn = do_syntax(job, wd, 'candidate_src.py')
    if syn['status'] != 'ok':
        case.update(outcome='HARNESS_ERROR', cause='candidate does not compile: %s'
                    % syn.get('cause'))
        return case
    b = do_behavior(job, wd, (ref_proc, ref_obs), 'candidate_src.py')
    if b['status'] == 'harness_error':
        case.update(outcome='HARNESS_ERROR', cause=b.get('cause'))
        return case
    detected = b['status'] == 'fail'
    case['detected'] = detected
    case['channels'] = b.get('channels', [])
    case['detail'] = b.get('first_difference') or b.get('cause')
    if job['expect'] == 'match':
        case['outcome'] = 'OK' if not detected else 'FALSE_POSITIVE'
    elif job['expect'] == 'detect':
        case['outcome'] = 'DETECTED' if detected else 'MISSED'
        if detected and job.get('channel') and job['channel'] not in case['channels']:
            case['outcome'] = 'DETECTED_OTHER_CHANNEL'
    else:  # mutation is dead at this optimization level
        case['outcome'] = 'OK_NOT_EXPECTED' if not detected else 'DETECTED_UNEXPECTEDLY'
    return case


# ------------------------------------------------------------- job building

def suite_spec(suite):
    """A named suite, or NAME=DIR: every DIR/*.py compiled and decompiled up to
    the syntax stage and never executed (e.g. a pull request's own test inputs)."""
    if suite in SUITES:
        return SUITES[suite]
    name, sep, root = suite.partition('=')
    if not sep or not name or name in SUITES or not os.path.isdir(root):
        sys.exit('unknown suite %r (use one of %s, or NAME=DIR)' % (suite, ', '.join(SUITES)))
    return {'root': os.path.realpath(root), 'pattern': '*.py', 'behavior': False}


def suite_name(suite):
    return suite.partition('=')[0]


def discover(suite, filters):
    spec = suite_spec(suite)
    name = suite_name(suite)
    found = []
    for path in sorted(glob.glob(os.path.join(spec['root'], spec['pattern']))):
        fid = os.path.relpath(path, spec['root'])[:-3].replace(os.sep, '/')
        if filters and not any(f in fid for f in filters):
            continue
        meta = read_header(path) if suite == 'features' else {}
        category = fid.split('/')[0] if '/' in fid else 'upstream'
        found.append({'suite': name, 'id': fid, 'path': path, 'category': category,
                      'meta': meta, 'behavior': spec['behavior']})
    return found


def common_setup(args):
    interps = resolve_interpreters(args.install_dir, dict(
        kv.split('=', 1) for kv in (args.python or [])),
        args.versions.split(',') if args.versions else None)
    mode = args.sandbox or sandbox.default_mode()
    if mode is None:
        sys.exit('no sandbox available on this platform; pass --sandbox none '
                 '--allow-unisolated to run without isolation (recorded in results)')
    if mode == 'none' and not args.allow_unisolated:
        sys.exit('--sandbox none requires --allow-unisolated')
    workroot = os.path.realpath(args.workroot)
    os.makedirs(workroot, exist_ok=True)
    read_allow = {REPO, os.path.expanduser(args.install_dir or load_config()['install_dir'])}
    for e in interps.values():
        if e.get('path'):
            read_allow.add(os.path.dirname(os.path.dirname(os.path.realpath(e['path']))))
    return interps, mode, workroot, read_allow


def base_job(fx, minor, entry, opt, mode, read_allow, workdir):
    return {'suite': fx['suite'], 'id': fx['id'], 'path': fx['path'],
            'category': fx['category'], 'behavior': fx['behavior'], 'minor': minor,
            'python': entry['path'], 'magic': entry['magic'], 'opt': opt, 'sandbox': mode,
            'read_allow': sorted(read_allow), 'workdir': workdir}


def skipped_case(fx, minor, opt, outcome, cause):
    return {'suite': fx['suite'], 'fixture': fx['id'], 'category': fx['category'],
            'version': minor, 'opt': opt, 'outcome': outcome, 'cause': cause}


def execute(fn, jobs, n):
    results = []
    total = len(jobs)
    with concurrent.futures.ProcessPoolExecutor(max_workers=n) as pool:
        futures = [pool.submit(fn, j) for j in jobs]
        for i, fut in enumerate(concurrent.futures.as_completed(futures), 1):
            results.append(fut.result())
            if i % 50 == 0 or i == total:
                sys.stderr.write('  %d/%d cases\n' % (i, total))
    return results


def meta_block(args, interps, mode, prov, kind):
    return {
        'kind': kind,
        'command': ['harness/difftest.py'] + sys.argv[1:],
        'created_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'host': {'platform': platform.platform(), 'machine': platform.machine(),
                 'harness_python': platform.python_version()},
        'sandbox': mode,
        'opt_levels': opt_list(args.opt),
        'interpreters': interps,
        'provenance': prov,
        'timeouts': TIMEOUTS,
    }


def scrub_paths(text):
    """Machine-specific absolute paths become <repo> and ~ in written results."""
    home = os.path.realpath(os.path.expanduser('~'))
    return text.replace(REPO, '<repo>').replace(home, '~')


def write_results(path, meta, cases):
    """Valid JSON laid out as indented metadata plus one compact line per case,
    so frozen baselines stay small and diff per case."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w') as f:
        f.write(scrub_paths('{"schema": 1,\n"meta": %s,\n"cases": [\n'
                            % json.dumps(meta, indent=1, sort_keys=True)))
        f.write(scrub_paths(',\n'.join(json.dumps(c, sort_keys=True, separators=(',', ':'))
                                       for c in cases)))
        f.write('\n]}\n')


# ----------------------------------------------------------------- commands

def cmd_interpreters(args):
    interps = resolve_interpreters(args.install_dir, dict(
        kv.split('=', 1) for kv in (args.python or [])))
    for e in interps.values():
        print('%-5s %-8s magic %-5s %-8s %s' % (e['minor'], e['pinned'], e['magic'],
                                                e['status'], e.get('path') or e.get('reason')))
    return 0 if all(e['status'] == 'ok' for e in interps.values()) else 1


def cmd_run(args):
    interps, mode, workroot, read_allow = common_setup(args)
    pycdc = os.path.realpath(args.pycdc)
    pycdas = os.path.realpath(args.pycdas or os.path.join(os.path.dirname(pycdc), 'pycdas'))
    source_root = os.path.realpath(args.source_root or REPO)
    read_allow.update({source_root, os.path.dirname(pycdc), os.path.dirname(pycdas)})
    probe = build_load_probe(source_root, os.path.dirname(pycdc), workroot)
    prov = provenance(source_root, {'pycdc': pycdc, 'pycdas': pycdas,
                                    'libpycxx': os.path.join(os.path.dirname(pycdc),
                                                             'libpycxx.a')})
    filters = args.filter.split(',') if args.filter else None
    jobs, cases = [], []
    for suite in args.suite.split(','):
        for fx in discover(suite, filters):
            for minor, entry in interps.items():
                for opt in opt_list(args.opt):
                    if not applicable(fx['meta'].get('requires'), minor):
                        cases.append(skipped_case(fx, minor, opt, 'N/A',
                                                  'requires ' + fx['meta']['requires']))
                        continue
                    if entry['status'] != 'ok':
                        cases.append(skipped_case(fx, minor, opt, 'MISSING',
                                                  'interpreter %s: %s' % (
                                                      entry['status'], entry.get('reason'))))
                        continue
                    wd = os.path.join(workroot, fx['suite'], fx['id'].replace('/', '__'),
                                      '%s-O%d' % (minor, opt))
                    job = base_job(fx, minor, entry, opt, mode, read_allow, wd)
                    job.update(pycdc=pycdc, pycdas=pycdas, load_probe=probe)
                    jobs.append(job)
    sys.stderr.write('running %d cases (%d skipped) with %d jobs, sandbox=%s\n'
                     % (len(jobs), len(cases), args.jobs, mode))
    start = time.monotonic()
    cases.extend(execute(run_case, jobs, args.jobs))
    meta = meta_block(args, interps, mode, prov, 'run')
    meta['suites'] = [suite_name(s) for s in args.suite.split(',')]
    meta['suite_roots'] = {suite_name(s): suite_spec(s)['root'] for s in args.suite.split(',')}
    meta['wall_seconds'] = round(time.monotonic() - start, 1)
    write_results(args.out, meta, sorted(cases, key=case_key))
    sys.stderr.write('wrote %s\n' % args.out)
    if args.summary:
        with open(args.summary, 'w') as f:
            f.write(render_summary(load_results(args.out)))
    return 0


def cmd_controls(args):
    interps, mode, workroot, read_allow = common_setup(args)
    prov = provenance(REPO, {})
    filters = args.filter.split(',') if args.filter else None
    fixtures = {fx['id']: fx for fx in discover('features', None)}
    jobs, cases = [], []

    def add(fx, candidate, expect_for_opt, control=None, channel=None):
        for minor, entry in interps.items():
            for opt in opt_list(args.opt):
                if not applicable(fx['meta'].get('requires'), minor):
                    continue
                if entry['status'] != 'ok':
                    cases.append(skipped_case(fx, minor, opt, 'MISSING', entry.get('reason')))
                    continue
                tag = control or 'positive'
                wd = os.path.join(workroot, 'controls', tag.replace('/', '__'),
                                  fx['id'].replace('/', '__'), '%s-O%d' % (minor, opt))
                job = base_job(fx, minor, entry, opt, mode, read_allow, wd)
                job.update(candidate=candidate, expect=expect_for_opt(opt), control=control,
                           channel=channel)
                jobs.append(job)

    if not args.negative_only:
        for fx in fixtures.values():
            if filters and not any(f in fx['id'] for f in filters):
                continue
            add(fx, fx['path'], lambda opt: 'match')
    src_dir = os.path.join(workroot, 'controls', '_sources')
    os.makedirs(src_dir, exist_ok=True)
    with open(os.path.join(HARNESS, 'controls', 'controls.json')) as f:
        controls = json.load(f)['controls']
    for ctl in controls:
        if filters and not any(f in ctl['id'] or f in ctl['fixture'] for f in filters):
            continue
        fx = fixtures.get(ctl['fixture'])
        if fx is None:
            sys.exit('control %s: unknown fixture %r' % (ctl['id'], ctl['fixture']))
        with open(fx['path'], encoding='utf-8') as f:
            original = f.read()
        if original.count(ctl['old']) != 1:
            sys.exit('control %s: replacement text occurs %d times in %s (must be exactly 1)'
                     % (ctl['id'], original.count(ctl['old']), ctl['fixture']))
        path = os.path.join(src_dir, ctl['id'] + '.py')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(original.replace(ctl['old'], ctl['new']))
        live = ctl.get('detect_at', [0, 1, 2])
        add(fx, path, lambda opt, live=live: 'detect' if opt in live else 'dead',
            control=ctl['id'], channel=ctl['channel'])
    sys.stderr.write('running %d control cases with %d jobs, sandbox=%s\n'
                     % (len(jobs), args.jobs, mode))
    start = time.monotonic()
    cases.extend(execute(run_control_case, jobs, args.jobs))
    meta = meta_block(args, interps, mode, prov, 'controls')
    meta['wall_seconds'] = round(time.monotonic() - start, 1)
    cases.sort(key=lambda c: (c.get('control') or '', c['fixture'], version_tuple(c['version']),
                              c['opt']))
    write_results(args.out, meta, cases)
    if args.summary:
        with open(args.summary, 'w') as f:
            f.write(render_controls(load_results(args.out)))
    bad = [c for c in cases if c['outcome'] not in ('OK', 'DETECTED', 'OK_NOT_EXPECTED')]
    sys.stderr.write('wrote %s; %d unexpected control outcomes\n' % (args.out, len(bad)))
    return 1 if bad else 0


STAGE_RANK = {s: i for i, s in enumerate(('compile', 'reference') + STAGES)}


def cmd_compare(args):
    base, new = load_results(args.baseline), load_results(args.results)
    groups = compare_groups(base, new)

    def desc(c):
        if c is None:
            return '-'
        if c['outcome'] == 'FAIL':
            return 'FAIL@%s/%s: %s' % (c.get('stage'), c.get('kind'), c.get('cause'))
        return c['outcome']

    print('baseline: %s (%s)' % (args.baseline, base['meta']['created_utc']))
    print('results:  %s (%s)' % (args.results, new['meta']['created_utc']))
    for name, items in groups.items():
        print('%-16s %d' % (name, len(items)))
    for name in ('regression', 'fixed', 'failure_changed', 'missing_coverage',
                 'harness_error', 'added', 'removed', 'corpus_drift'):
        for key, b, n in groups[name][:args.limit]:
            print('  [%s] %s %s %s-O%d: %s -> %s' % (name, key[0], key[1],
                                                    '.'.join(map(str, key[2])), key[3],
                                                    desc(b), desc(n)))
    return 1 if groups['regression'] or groups['missing_coverage'] or \
        groups['harness_error'] else 0


def compare_groups(base, new):
    bidx = {case_key(c): c for c in base['cases']}
    nidx = {case_key(c): c for c in new['cases']}
    groups = collections.OrderedDict((k, []) for k in (
        'regression', 'fixed', 'still_failing', 'failure_changed', 'unchanged_pass',
        'not_applicable', 'missing_coverage', 'harness_error', 'added', 'removed',
        'corpus_drift'))
    for key in sorted(set(bidx) | set(nidx)):
        b, n = bidx.get(key), nidx.get(key)
        if b is None:
            groups['added'].append((key, None, n))
            continue
        if n is None:
            groups['removed'].append((key, b, None))
            continue
        if b.get('hashes', {}).get('pyc') and n.get('hashes', {}).get('pyc') and \
                b['hashes']['pyc'] != n['hashes']['pyc']:
            groups['corpus_drift'].append((key, b, n))
        bo, no = b['outcome'], n['outcome']
        if no == 'MISSING':
            groups['missing_coverage'].append((key, b, n))
        elif no == 'HARNESS_ERROR':
            groups['harness_error'].append((key, b, n))
        elif bo == 'N/A' and no == 'N/A':
            groups['not_applicable'].append((key, b, n))
        elif bo == 'PASS' and no == 'PASS':
            groups['unchanged_pass'].append((key, b, n))
        elif bo == 'PASS':
            groups['regression'].append((key, b, n))
        elif no == 'PASS':
            groups['fixed'].append((key, b, n))
        elif (b.get('stage'), b.get('kind'), b.get('cause')) == \
                (n.get('stage'), n.get('kind'), n.get('cause')):
            groups['still_failing'].append((key, b, n))
        elif STAGE_RANK.get(n.get('stage'), 99) < STAGE_RANK.get(b.get('stage'), 99):
            groups['regression'].append((key, b, n))
        else:
            groups['failure_changed'].append((key, b, n))
    return groups


def load_requirements():
    with open(os.path.join(HARNESS, 'requirements.json')) as f:
        return json.load(f)


def part_of(req):
    owner = {}
    for part, spec in req['parts'].items():
        if spec['fixtures'] != '*':
            for fid in spec['fixtures']:
                owner[fid] = part
    return owner


def meets(case, required_stage):
    if case['outcome'] == 'PASS':
        return required_stage != 'behavior' or case.get('validated_to') == 'behavior'
    if case['outcome'] != 'FAIL':
        return False
    return STAGE_RANK.get(case['stage'], -1) > STAGE_RANK[required_stage]


def cmd_gate(args):
    """Mechanical completion-gate check for Parts 4-7 (see requirements.json)."""
    req = load_requirements()
    res = load_results(args.results)
    meta, problems = res['meta'], []
    if meta['kind'] != 'run':
        problems.append('results file is not a "run" results file')
    for suite in req['required_suites']:
        if suite not in meta.get('suites', []):
            problems.append('suite %s was not run' % suite)
    if sorted(meta['opt_levels']) != sorted(req['opt_levels']):
        problems.append('optimization levels %s != required %s' % (meta['opt_levels'],
                                                                   req['opt_levels']))
    for v in req['required_versions'] + req['regression_versions']:
        e = meta['interpreters'].get(v)
        if not e or e.get('status') != 'ok':
            problems.append('interpreter %s not available in this run' % v)
    if meta['provenance'].get('harness_dirty'):
        problems.append('harness files were modified when the results were produced')

    idx = {(c['suite'], c['fixture'], c['version'], c['opt']): c for c in res['cases']}
    all_features = [fx['id'] for fx in discover('features', None)]
    print('gate for Part %s (requirements of Parts 4..%s)' % (args.part, args.part))
    for part in sorted(req['parts'], key=int):
        if int(part) > int(args.part):
            continue
        spec = req['parts'][part]
        fixtures = all_features if spec['fixtures'] == '*' else spec['fixtures']
        total, unmet = 0, []
        for fid in fixtures:
            for v in req['required_versions']:
                for opt in req['opt_levels']:
                    c = idx.get(('features', fid, v, opt))
                    if c is None:
                        unmet.append('%s %s-O%d: case missing from results' % (fid, v, opt))
                        continue
                    if c['outcome'] == 'N/A':
                        continue
                    total += 1
                    if not meets(c, spec['required_stage']):
                        unmet.append('%s %s-O%d: %s %s' % (
                            fid, v, opt, c['outcome'],
                            '@%s/%s: %s' % (c.get('stage'), c.get('kind'), c.get('cause'))
                            if c['outcome'] == 'FAIL' else c.get('cause', '')))
        print('  Part %s (%s): %d/%d required cases reach %s' % (
            part, spec['title'], total - len(unmet), total, spec['required_stage']))
        for line in unmet[:args.limit]:
            print('    unmet: ' + line)
        if len(unmet) > args.limit:
            print('    ... %d more' % (len(unmet) - args.limit))
        problems.extend('Part %s requirement unmet: %s' % (part, u) for u in unmet)
        for note in spec.get('not_yet_mechanized', []):
            print('    manual evidence required: ' + note)

    groups = compare_groups(load_results(args.baseline), res)
    for name in ('regression', 'missing_coverage', 'harness_error'):
        print('  vs baseline: %s %d' % (name, len(groups[name])))
        problems.extend('%s: %s' % (name, k) for k, _, _ in groups[name])

    ctl = load_results(args.controls)
    bad = [c for c in ctl['cases'] if c['outcome'] not in ('OK', 'DETECTED', 'OK_NOT_EXPECTED')]
    print('  controls: %d cases, %d unexpected' % (len(ctl['cases']), len(bad)))
    if bad:
        problems.append('%d unexpected control outcomes' % len(bad))

    with open(args.upstream_baseline) as f:
        ub = {r['file']: r['outcome'] for r in json.load(f)['results']}
    with open(args.upstream) as f:
        un = {r['file']: r['outcome'] for r in json.load(f)['results']}
    upstream_reg = sorted(k for k, o in ub.items() if o == 'PASS' and un.get(k) != 'PASS')
    print('  upstream token suite: %d previously passing files no longer pass'
          % len(upstream_reg))
    problems.extend('upstream token suite regression: ' + k for k in upstream_reg)

    print('GATE %s (%d problems)' % ('PASSED' if not problems else 'NOT PASSED', len(problems)))
    return 0 if not problems else 1


def cmd_list(args):
    req = load_requirements()
    owner = part_of(req)
    print('| fixture | part | requires | summary |')
    print('| --- | --- | --- | --- |')
    for fx in discover('features', None):
        print('| `%s` | %s | %s | %s |' % (fx['id'], owner.get(fx['id'], '**unassigned**'),
                                         fx['meta'].get('requires', 'all'),
                                         fx['meta'].get('summary', '')))
    return 0


def cmd_summarize(args):
    data = load_results(args.results)
    if data['meta']['kind'] == 'controls':
        sys.stdout.write(render_controls(data))
    else:
        sys.stdout.write(render_summary(data))
    return 0


# ---------------------------------------------------------------- reporting

def load_results(path):
    with open(path) as f:
        return json.load(f)


def meta_lines(meta):
    prov = meta['provenance']
    lines = ['| | |', '| --- | --- |',
             '| created (UTC) | %s |' % meta['created_utc'],
             '| command | `%s` |' % ' '.join(meta['command']),
             '| host | %s, harness Python %s |' % (meta['host']['platform'],
                                                  meta['host']['harness_python']),
             '| sandbox | %s |' % meta['sandbox'],
             '| optimization levels | %s |' % ', '.join(map(str, meta['opt_levels']))]
    if prov.get('source_head'):
        lines.append('| decompiler source | `%s` (%s), dirty files: %s |' % (
            prov['source_head'], prov.get('source_branch'),
            ', '.join(prov['decompiler_source_dirty']) or 'none'))
    lines.append('| harness | `%s`, dirty files: %s |' % (
        prov['harness_head'], len(prov['harness_dirty'])))
    for name, b in sorted(prov.get('binaries', {}).items()):
        lines.append('| %s | sha256 `%s` |' % (name, b['sha256']))
    for e in meta['interpreters'].values():
        lines.append('| CPython %s | %s, magic %s, %s |' % (e['minor'], e['pinned'],
                                                          e['magic'], e['status']))
    if 'wall_seconds' in meta:
        lines.append('| wall time | %ss |' % meta['wall_seconds'])
    return lines


def render_summary(data):
    meta, cases = data['meta'], data['cases']
    out = ['# Differential test results', ''] + meta_lines(meta) + ['']
    versions = sorted({c['version'] for c in cases}, key=version_tuple)
    cols = ['PASS'] + ['FAIL@' + s for s in STAGES] + ['crash', 'timeout', 'incomplete',
                                                       'N/A', 'MISSING', 'HARNESS_ERROR']
    for suite in meta.get('suites', sorted({c['suite'] for c in cases})):
        sc = [c for c in cases if c['suite'] == suite]
        if not sc:
            continue
        policy = 'behavior' if SUITES.get(suite, {}).get('behavior') else 'syntax (not executed)'
        out += ['## Suite `%s` — validated up to: %s' % (suite, policy), '',
                'Every case is counted once, at its earliest failing stage. crash, '
                'timeout and incomplete are subsets of the FAIL columns.', '',
                '| version | cases | ' + ' | '.join(cols) + ' |',
                '| --- | --- | ' + ' | '.join('---' for _ in cols) + ' |']
        for v in versions + ['all']:
            vc = sc if v == 'all' else [c for c in sc if c['version'] == v]
            counts = collections.Counter()
            for c in vc:
                if c['outcome'] == 'FAIL':
                    counts['FAIL@' + c['stage']] += 1
                    if c.get('kind') in ('crash', 'timeout', 'incomplete'):
                        counts[c['kind']] += 1
                else:
                    counts[c['outcome']] += 1
            out.append('| %s | %d | %s |' % (v, len(vc), ' | '.join(str(counts[k]) for k in cols)))
        out.append('')
        if suite == 'features':
            out += render_categories(sc, versions)
        out += render_opt(sc, versions)
        out += render_timing(sc, versions)
        out += render_causes(sc)
    return '\n'.join(out) + '\n'


def render_timing(cases, versions):
    out = ['### Stage wall time in seconds: total / median per case (cases where the stage ran)',
           '', 'behavior times the candidate run only; the reference run is not included.', '',
           '| stage | ' + ' | '.join(versions) + ' |',
           '| --- | ' + ' | '.join('---' for _ in versions) + ' |']
    for st in ('compile',) + STAGES:
        cells = []
        for v in versions:
            secs = sorted(c['stages'][st]['seconds'] for c in cases
                          if c['version'] == v and st in c.get('stages', {})
                          and 'seconds' in c['stages'][st])
            cells.append('%.1f / %.3f' % (sum(secs), secs[len(secs) // 2]) if secs else '-')
        out.append('| %s | %s |' % (st, ' | '.join(cells)))
    return out + ['']


def render_categories(cases, versions):
    out = ['### PASS / applicable cases by category (all optimization levels)', '',
           '| category | ' + ' | '.join(versions) + ' |',
           '| --- | ' + ' | '.join('---' for _ in versions) + ' |']
    for cat in sorted({c['category'] for c in cases}):
        cells = []
        for v in versions:
            vc = [c for c in cases if c['category'] == cat and c['version'] == v
                  and c['outcome'] not in ('N/A',)]
            if not vc:
                cells.append('n/a')
                continue
            cells.append('%d/%d' % (sum(c['outcome'] == 'PASS' for c in vc), len(vc)))
        out.append('| %s | %s |' % (cat, ' | '.join(cells)))
    return out + ['']


def render_opt(cases, versions):
    out = ['### PASS / applicable cases by optimization level', '',
           '| opt | ' + ' | '.join(versions) + ' |',
           '| --- | ' + ' | '.join('---' for _ in versions) + ' |']
    for opt in sorted({c['opt'] for c in cases}):
        cells = []
        for v in versions:
            vc = [c for c in cases if c['opt'] == opt and c['version'] == v
                  and c['outcome'] != 'N/A']
            cells.append('%d/%d' % (sum(c['outcome'] == 'PASS' for c in vc), len(vc))
                         if vc else 'n/a')
        out.append('| -O%d | %s |' % (opt, ' | '.join(cells)))
    return out + ['']


def render_causes(cases, top=12):
    out = ['### Most frequent failure causes per stage', '']
    for st in STAGES:
        fc = [c for c in cases if c['outcome'] == 'FAIL' and c['stage'] == st]
        if not fc:
            continue
        counter = collections.Counter((c.get('kind'), c.get('cause')) for c in fc)
        out += ['**%s** (%d cases)' % (st, len(fc)), '', '| count | kind | cause | versions |',
                '| --- | --- | --- | --- |']
        for (kind, cause), n in counter.most_common(top):
            vs = sorted({c['version'] for c in fc if (c.get('kind'), c.get('cause'))
                         == (kind, cause)}, key=version_tuple)
            out.append('| %d | %s | %s | %s |' % (n, kind, str(cause).replace('|', '\\|')[:150],
                                                 ', '.join(vs)))
        if len(counter) > top:
            out.append('| … | | %d more distinct causes | |' % (len(counter) - top))
        out.append('')
    return out


def render_controls(data):
    meta, cases = data['meta'], data['cases']
    out = ['# Harness control results', ''] + meta_lines(meta) + ['']
    pos = [c for c in cases if c.get('expect') == 'match']
    neg = [c for c in cases if c.get('control')]
    pc = collections.Counter(c['outcome'] for c in pos)
    out += ['## Positive controls (original source as candidate; must match)', '',
            '%d cases: %s' % (len(pos), ', '.join('%s=%d' % kv for kv in sorted(pc.items()))), '']
    bad = [c for c in pos if c['outcome'] != 'OK']
    for c in bad[:30]:
        out.append('- %s %s-O%d: %s %s' % (c['fixture'], c['version'], c['opt'], c['outcome'],
                                          c.get('detail') or c.get('cause')))
    out += ['', '## Negative controls (deliberate semantic changes; must be detected)', '',
            '| control | fixture | declared channel | expected | outcome counts | channels seen |',
            '| --- | --- | --- | --- | --- | --- |']
    for cid in sorted({c['control'] for c in neg}):
        cc = [c for c in neg if c['control'] == cid]
        counts = collections.Counter(c['outcome'] for c in cc)
        seen = sorted({ch for c in cc for ch in c.get('channels', [])})
        expected = sorted({'%s@O%d' % (c['expect'], c['opt']) for c in cc})
        out.append('| %s | %s | %s | %s | %s | %s |' % (
            cid, cc[0]['fixture'], cc[0].get('channel'), ', '.join(sorted({c['expect'] for c in cc})),
            ', '.join('%s=%d' % kv for kv in sorted(counts.items())), ', '.join(seen)))
    nbad = [c for c in neg if c['outcome'] not in ('DETECTED', 'OK_NOT_EXPECTED')]
    out += ['', 'Unexpected negative-control outcomes: %d' % len(nbad)]
    for c in nbad[:30]:
        out.append('- %s on %s %s-O%d: %s %s' % (c['control'], c['fixture'], c['version'],
                                                c['opt'], c['outcome'],
                                                c.get('detail') or c.get('cause')))
    return '\n'.join(out) + '\n'


# --------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)

    def common(p):
        p.add_argument('--install-dir', help='pinned interpreter directory '
                       '(default from interpreters.json)')
        p.add_argument('--python', action='append', metavar='X.Y=PATH',
                       help='override an interpreter path (still version-verified)')
        p.add_argument('--versions', help='comma-separated subset, e.g. 3.13,3.14')
        p.add_argument('--opt', default='0,1,2', help='optimization levels (default 0,1,2)')
        p.add_argument('--filter', help='comma-separated substrings of fixture ids')
        p.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
        p.add_argument('--sandbox', choices=['macos-sandbox-exec', 'none'])
        p.add_argument('--allow-unisolated', action='store_true')
        p.add_argument('--workroot', default=os.path.join(REPO, 'build', 'difftest'))
        p.add_argument('--out', required=True, help='results JSON path')
        p.add_argument('--summary', help='also write a Markdown summary here')

    p = sub.add_parser('interpreters')
    p.add_argument('--install-dir')
    p.add_argument('--python', action='append', metavar='X.Y=PATH')
    p.set_defaults(fn=cmd_interpreters)

    p = sub.add_parser('run')
    common(p)
    p.add_argument('--pycdc', default=os.path.join(REPO, 'build', 'release', 'pycdc'))
    p.add_argument('--pycdas', help='default: next to --pycdc')
    p.add_argument('--source-root', help='source tree the binaries were built from '
                   '(default: this repository)')
    p.add_argument('--suite', default='features', help='comma-separated: '
                   + ', '.join(SUITES) + ', or NAME=DIR (compiled and decompiled, '
                   'never executed)')
    p.set_defaults(fn=cmd_run)

    p = sub.add_parser('controls')
    common(p)
    p.add_argument('--negative-only', action='store_true')
    p.set_defaults(fn=cmd_controls)

    p = sub.add_parser('compare')
    p.add_argument('baseline')
    p.add_argument('results')
    p.add_argument('--limit', type=int, default=200)
    p.set_defaults(fn=cmd_compare)

    p = sub.add_parser('summarize')
    p.add_argument('results')
    p.set_defaults(fn=cmd_summarize)

    p = sub.add_parser('gate', help='check a completion gate against requirements.json')
    p.add_argument('--part', required=True, choices=['4', '5', '6', '7'])
    p.add_argument('--results', required=True, help='run results (all suites, versions, -O levels)')
    p.add_argument('--controls', required=True, help='controls results from the same harness')
    p.add_argument('--upstream', required=True,
                   help='per_file_outcomes.py --json output for the build under test')
    p.add_argument('--baseline', default=os.path.join(REPO, 'reports', 'part2-baseline',
                                                      'baseline.json'))
    p.add_argument('--upstream-baseline', default=os.path.join(
        REPO, 'reports', 'part1-baseline', 'per_file_outcomes.json'))
    p.add_argument('--limit', type=int, default=40)
    p.set_defaults(fn=cmd_gate)

    p = sub.add_parser('list', help='print the fixture matrix as Markdown')
    p.set_defaults(fn=cmd_list)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == '__main__':
    sys.exit(main())
