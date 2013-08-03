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
    if exename not in os.listdir(path):
        raise ValueError('invalid command %s (not in %s)' % (exename, path))
    return generic_call([path + '/' + exename] + args, **kwargs)

def run_hooks(path, args, **kwargs):
    if os.path.exists(path):
        for name in os.listdir(path):
            generic_call([path + '/' + name] + args, **kwargs)

def generic_call(*args, **kwargs):
    func = kwargs.setdefault('func', subprocess.check_call)
    del kwargs['func']
    return func(*args, **kwargs)

def check_if_valid_path_entry(name):
    ok = name.decode('ascii') == name and '/' not in name and '\0' not in name
    if not ok:
        raise ValueError('invalid path name %r' % name)

def chdir_to_code():
    dir = os.path.dirname(os.path.realpath(sys.argv[0]))
    os.chdir(dir)

def call_with_stdin(args, **kwargs):
    assert kwargs.get('stdout') != subprocess.PIPE
    kwargs.update(dict(
        stdin=subprocess.PIPE
    ))
    stdin_data = kwargs['stdin_data']
    del kwargs['stdin_data']
    popen = subprocess.Popen(args, **kwargs)
    popen.stdin.write(stdin_data)
    popen.stdin.flush()
    retcode = popen.wait()
    if retcode != 0:
        raise subprocess.CalledProcessError(retcode, args)

def run_editor(text):
    import tempfile
    f = tempfile.NamedTemporaryFile()
    f.write(text)
    f.flush()
    try:
        subprocess.check_call([os.environ.get('EDITOR', 'nano'), f.name])
        with open(f.name) as f:
            return f.read()
    finally:
        f.close()

def run_yaml_editor(comment, object, check_func=None):
    import yaml
    import traceback
    comment = '# You are editing YAML document which will be parsed and ' \
              'serialized to BSON.\n# Any comments are not going to be saved. ' \
              'Leave document empty to abort.' \
              '\n#\n# ' + comment + '\n'
    text = comment + yaml.safe_dump(object)
    while True:
        text = run_editor(text)
        try:
            result = yaml.safe_load(text)
            if check_func:
                check_func(result)
        except:
            text = '# ' + traceback.format_exc().replace('\n', '\n# ') + '\n' + text
        else:
            if result is None:
                raise Exception('aborted')
            return result
