#!/usr/bin/env python
import argparse
import gravelrpc
from gravelrpc import FD

parser = argparse.ArgumentParser()
parser.add_argument('--ssl', action='store_true')
parser.add_argument('--ssl-key', default='example.pem')
parser.add_argument('name')
parser.add_argument('expression')
args = parser.parse_args()

if args.ssl:
    host, port = args.name.split(':')
    client = gravelrpc.SSLClient((host, int(port)), args.ssl_key)
else:
    client = gravelrpc.Client(args.name)
print eval('client.' + args.expression)
