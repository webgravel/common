import sys
import os
import subprocess

def main_multiple_action(globals):
    actions = [ k[len('action_'):] for k in globals.keys() if k.startswith('action_') ]
    if len(sys.argv) < 2 or sys.argv[1] not in actions:
        sys.exit('Usage: {} {} ...'.format(sys.argv[0], '|'.join(actions)))
    action = sys.argv[1]
    del sys.argv[1:2]
    sys.argv[0] += ' ' + action
    globals['action_' + action]()

def call_exe_in_directory(path, exename, args, **kwargs):
    func = kwargs.setdefault('func', subprocess.check_call)
    del kwargs['func']
    if exename not in os.listdir(path):
        raise ValueError('invalid command %s (not in %s)' % (exename, path))
    return func([path + '/' + exename] + args, **kwargs)

def check_if_valid_path_entry(name):
    ok = name.decode('ascii') == name and '/' not in name and '\0' not in name
    if not ok:
        raise ValueError('invalid path name %r' % name)

def chdir_to_code():
    dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(dir)
