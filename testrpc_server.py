import gravelrpc

class Handler(gravelrpc.RPCHandler):
	def method_hello(self, name):
		return 'Hello, %s!' % name

Handler.main('foo')
