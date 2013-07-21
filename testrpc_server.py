import gravelrpc

class Handler(gravelrpc.RPCHandler):
    allow_fd_passing = True

    def method_hello(self, name):
        return 'Hello, %s!' % name

    def method_say_hello(self, _fds):
        stdout, = _fds
        stdout.open('w').write('HELLO!')

Handler.main('foo')
