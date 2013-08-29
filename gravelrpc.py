import SocketServer
import socket
import functools
import os
import traceback
import passfd
import struct
import ssl

import bson as _bson
from bson.binary import Binary

PATH = '/gravel/run/%s.sock'

class ThreadingUnixServer(SocketServer.ThreadingMixIn, SocketServer.UnixStreamServer):
    def server_bind(self):
        if os.path.exists(self.server_address):
            os.remove(self.server_address)
        SocketServer.UnixStreamServer.server_bind(self)

class ThreadingSSLServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    key = 'example.pem' # TODO

    def server_bind(self):
        self.socket = ssl.wrap_socket(self.socket, certfile=self.key, server_side=True)
        SocketServer.TCPServer.server_bind(self)

class RPCHandler(SocketServer.StreamRequestHandler):
    allow_fd_passing = False

    def handle(self):
        req = _rpc_read_bson(self.request, allow_fd_passing=self.allow_fd_passing)
        try:
            if 'fds' in req:
                req['kwargs']['_fds'] = req['fds']
            result = getattr(self, 'method_' + req['name'])(*req['args'], **req['kwargs'])
        except Exception as err:
            traceback.print_exc()
            doc = dict(error=str(err))
        else:
            doc = dict(result=result)
        _rpc_write_bson(self.request, doc)

    @classmethod
    def main(cls, name, server=None):
        if server is None:
            name = PATH % name
            server = ThreadingUnixServer
        serv = server(name, cls)
        serv.serve_forever()

class RPCError(Exception): pass

class GenericClient(object):
    def _call(self, name, *args, **kwargs):
        sock = self._connect()
        doc = dict(name=name, args=args, kwargs=kwargs)
        if '_fds' in kwargs:
            doc['fds'] = kwargs['_fds']
            kwargs['_fds'] = None
        _rpc_write_bson(sock, doc)
        result = _rpc_read_bson(sock)
        if 'error' in result:
            raise RPCError(result['error'])
        return result['result']

    def __getattr__(self, name):
        return functools.partial(self._call, name)

class Client(GenericClient):
    def __init__(self, name):
        self._path = PATH % name

    def _connect(self):
        sock = socket.socket(socket.AF_UNIX)
        sock.connect(self._path)
        return sock

class SSLClient(GenericClient):
    def __init__(self, host, key):
        self._host = host
        self._key = key

    def _connect(self):
        sock = socket.socket()
        sock.connect(self._host)
        # TODO: key verification
        return ssl.wrap_socket(sock,
                               ca_certs=self._key,
                               cert_reqs=ssl.CERT_REQUIRED,
                               server_side=True)

class FD(object):
    def __init__(self, fileno):
        self._fileno = fileno

    def fileno(self):
        return self._fileno

    def open(self, *args, **kwargs):
        return os.fdopen(self.fileno(), *args, **kwargs)

def _rpc_write_bson(sock, doc):
    fds = doc.get('fds', [])
    doc['fds'] = len(fds)

    sock.send(struct.pack('!I', len(fds)))
    for fd in fds:
        if not isinstance(fd, FD):
            raise TypeError('fds need to be instances of FD (not %r)' % fd)
        passfd.sendfd(sock, fd.fileno(), 'whatever')

    sock.sendall(_bson.BSON.encode(doc))
    sock.shutdown(socket.SHUT_WR)

def _rpc_read_bson(sock, allow_fd_passing=False):
    fd_count, = struct.unpack('!I', sock.recv(4))

    if fd_count == 0 or allow_fd_passing:
        fds = [ FD(passfd.recvfd(sock)[0]) for i in xrange(fd_count) ]
    else:
        raise IOError('client tried to pass fds')

    raw = ''.join(iter(lambda: sock.recv(4096), ''))
    result = _bson.BSON(raw).decode()
    if fd_count != 0:
        result['fds'] = fds
    elif 'fds' in result:
        del result['fds']
    return result

class bson:
    ''' pickle/marshal/json compatiblity module for BSON '''
    def load(self, f):
        length_data = f.read(4)
        length, = struct.unpack('<I', length_data)
        return _bson.BSON(length_data + f.read(length - 4)).decode()

    def dump(self, obj, f):
        f.write(_bson.BSON.encode(obj))

    def loads(self, s):
        return _bson.BSON(s).decode()

    def dumps(self, obj):
        return _bson.BSON.encode(obj)

    Binary = Binary

bson = bson()
