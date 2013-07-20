import SocketServer
import socket
import functools
import bson
import os
import traceback

from bson.binary import Binary

PATH = '/gravel/run/%s.sock'

class ThreadingUnixServer(SocketServer.ThreadingMixIn, SocketServer.UnixStreamServer):
    def server_bind(self):
        if os.path.exists(self.server_address):
            os.remove(self.server_address)
        SocketServer.UnixStreamServer.server_bind(self)

class RPCHandler(SocketServer.StreamRequestHandler):
    def handle(self):
        req = bson.BSON(self.rfile.read()).decode()
        try:
            result = getattr(self, 'method_' + req['name'])(*req['args'], **req['kwargs'])
        except Exception as err:
            traceback.print_exc()
            doc = dict(error=str(err))
        else:
            doc = dict(result=result)
        self.wfile.write(bson.BSON.encode(doc))
        self.wfile.close()

    @classmethod
    def main(cls, name):
        path = PATH % name
        serv = ThreadingUnixServer(path, cls)
        serv.serve_forever()

class RPCError(Exception): pass

class Client(object):
    def __init__(self, name):
        self._path = PATH % name

    def _call(self, name, *args, **kwargs):
        sock = socket.socket(socket.AF_UNIX)
        sock.connect(self._path)
        f = sock.makefile('r', 0)
        doc = dict(name=name, args=args, kwargs=kwargs)
        sock.sendall(bson.BSON.encode(doc))
        sock.shutdown(socket.SHUT_WR)
        result = f.read()
        result = bson.BSON(result).decode()
        if 'error' in result:
            raise RPCError(result['error'])
        return result['result']

    def __getattr__(self, name):
        return functools.partial(self._call, name)
