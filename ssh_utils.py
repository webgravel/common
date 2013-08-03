import tempfile
import os
import urllib
import subprocess

def reformat_ssh_key(data):
    ''' Returns data as a well formed ssh-rsa key '''
    split = data.split(None, 2)
    if len(split) < 2:
        raise ValueError('Not enough values in SSH key.')

    if len(split) == 2:
        split = split + ['',]

    type, value, author = split

    if type != 'ssh-rsa':
        raise ValueError('Wrong key type.')

    data = value.decode('base64').encode('base64').replace('\n', '')
    author = urllib.quote(author.strip())

    return '%s %s %s' % (type, data, author)

def get_ssh_key_fingerprint(data):
    key = reformat_ssh_key(data).split(None, 2)[1]
    fp_plain = hashlib.md5(key).hexdigest()
    return ':'.join( a + b for a,b in zip(fp_plain[::2], fp_plain[1::2]) )

def write_authorized_keys(keys, user=''):
    '''
    Replaces autogenerated part of authorized_keys.
    Command from keys is not escaped in any way, but keys are!!!
    '''
    AUTOGEN_START = '### START AUTOGENERATED ###\n'
    AUTOGEN_END = '### END AUTOGENERATED ###\n'
    path = os.path.expanduser('~%s/.ssh/authorized_keys' % user)
    out = tempfile.NamedTemporaryFile(delete=False)

    if os.path.exists(path):
        autogen = False
        for line in open(path):
            if line == AUTOGEN_START:
                autogen = True
            elif line == AUTOGEN_END:
                autogen = False
            elif not autogen:
                out.write(line)

    out.write(AUTOGEN_START)
    for command, key in keys:
        escaped_key = reformat_ssh_key(key)
        out.write('command="%s",no-port-forwarding,no-X11-forwarding,no-agent-forwarding,no-pty %s\n'
                  % (command, escaped_key))
    out.write(AUTOGEN_END)
    out.close()
    os.rename(out.name, path)

def call(address, *args, **kwargs):
    def _get_kwargs(key=None, decode=None, check_output=True, func=None, **rest):
        return key, decode, check_output, func, rest

    key, decode, check_output, func, rest = _get_kwargs(**kwargs)
    if ':' in address:
        hostname, port = address.split(':')
    else:
        hostname = address
        port = None
    opts = ['-o', 'StrictHostKeyChecking=no', '-o', 'PasswordAuthentication=no']
    if key:
        opts += ['-i', key]
    if port:
        opts += ['-p', port]
    if not func:
        func = subprocess.check_output if check_output else subprocess.check_call
    result = func([
        'ssh', ] + opts + [hostname, '--'] + list(args), **rest)
    if decode:
        return decode.loads(result)
    else:
        return result
