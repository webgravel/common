# coding: utf-8
import gravelrpc
import sys

c = gravelrpc.Client('foo')
print c.hello(u'Michał!')

c.say_hello(_fds=[sys.stdout.fileno()])
