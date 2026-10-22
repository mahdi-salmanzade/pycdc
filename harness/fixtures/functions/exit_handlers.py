# feature: functions
# summary: atexit handlers run at interpreter exit (observed through the process stdout/stderr channels)
import atexit
import sys

state = {'calls': 0}


@atexit.register
def goodbye():
    print('atexit goodbye, calls =', state['calls'])


def to_stderr(msg):
    sys.stderr.write('atexit stderr: %s\n' % msg)


atexit.register(to_stderr, 'registered with argument')


def observe():
    state['calls'] += 1
    return state
