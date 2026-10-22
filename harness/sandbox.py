"""Isolated, resource-limited process execution for the harness.

Every process the harness starts for a test case (target-interpreter workers,
pycdc, pycdas, the load probe) goes through run().

- Environment: replaced by a fixed allowlist, so no credentials or tokens
  from the caller's environment reach the child.  HOME and TMPDIR point at
  the case work directory.
- macOS ("macos-sandbox-exec"): a sandbox-exec profile denies all network
  access, denies writes outside the case work directory, and denies reads
  under $HOME except for explicitly allowed paths (interpreters, repository).
- Resource limits: CPU seconds, maximum file size (stdout/stderr are files,
  so runaway output is bounded too), no core dumps; address space on Linux
  only (macOS does not enforce RLIMIT_AS, so memory there is bounded only by
  the CPU limit and wall-clock timeout).
- Wall-clock timeout; the whole process group is killed on expiry.

Mode "none" applies environment scrubbing, rlimits and timeouts but no
sandbox profile.  It must be requested explicitly and is recorded in results.
"""

import os
import resource
import signal
import subprocess
import sys
import time

SANDBOX_EXEC = '/usr/bin/sandbox-exec'
OUTPUT_LIMIT = 64 * 1024 * 1024
READ_LIMIT = 4 * 1024 * 1024


def default_mode():
    if sys.platform == 'darwin' and os.path.exists(SANDBOX_EXEC):
        return 'macos-sandbox-exec'
    return None


def _sbpl(path):
    return '"' + path.replace('\\', '\\\\').replace('"', '\\"') + '"'


def macos_profile(workdir, read_allow):
    home = os.path.realpath(os.path.expanduser('~'))
    allow = ' '.join('(subpath {})'.format(_sbpl(os.path.realpath(p)))
                     for p in list(read_allow) + [workdir])
    return '\n'.join([
        '(version 1)',
        '(allow default)',
        '(deny network*)',
        '(deny file-write*)',
        '(allow file-write* (subpath {}) (literal "/dev/null")'
        ' (literal "/dev/stdout") (literal "/dev/stderr")'
        ' (literal "/dev/dtracehelper"))'.format(_sbpl(workdir)),
        '(deny file-read* (subpath {}))'.format(_sbpl(home)),
        '(allow file-read* {})'.format(allow),
    ])


class Result(object):
    def __init__(self, returncode, stdout, stderr, timed_out, seconds):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.timed_out = timed_out
        self.seconds = seconds

    @property
    def signal(self):
        return -self.returncode if self.returncode is not None and self.returncode < 0 else None

    def signal_name(self):
        try:
            return signal.Signals(self.signal).name
        except (ValueError, TypeError):
            return str(self.signal)


def _limits(cpu_seconds):
    def apply():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds + 1))
        resource.setrlimit(resource.RLIMIT_FSIZE, (OUTPUT_LIMIT, OUTPUT_LIMIT))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        if sys.platform.startswith('linux'):
            limit = 2 * 1024 * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    return apply


def _read(path):
    with open(path, 'rb') as f:
        return f.read(READ_LIMIT)


def run(argv, workdir, mode, timeout, read_allow=(), env_extra=None, tag='proc'):
    """Run argv with cwd=workdir under the given isolation mode.

    stdout and stderr are written to <workdir>/<tag>.stdout / .stderr and
    returned as bytes (truncated at READ_LIMIT).
    """
    workdir = os.path.realpath(workdir)
    env = {'PATH': '/usr/bin:/bin', 'HOME': workdir, 'TMPDIR': workdir}
    if env_extra:
        env.update(env_extra)
    if mode == 'macos-sandbox-exec':
        full = [SANDBOX_EXEC, '-p', macos_profile(workdir, read_allow)] + list(argv)
    elif mode == 'none':
        full = list(argv)
    else:
        raise ValueError('unknown sandbox mode: {!r}'.format(mode))

    out_path = os.path.join(workdir, tag + '.stdout')
    err_path = os.path.join(workdir, tag + '.stderr')
    cpu = max(1, int(timeout))
    start = time.monotonic()
    with open(out_path, 'wb') as out, open(err_path, 'wb') as err:
        proc = subprocess.Popen(full, cwd=workdir, env=env, stdin=subprocess.DEVNULL,
                                stdout=out, stderr=err, start_new_session=True,
                                preexec_fn=_limits(cpu))
        timed_out = False
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
    seconds = time.monotonic() - start
    rc = proc.returncode
    if rc is not None and rc < 0 and -rc == signal.SIGXCPU:
        timed_out = True
    return Result(rc, _read(out_path), _read(err_path), timed_out, seconds)
