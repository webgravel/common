#!/usr/bin/env python
import argparse
import gravelrpc
from gravelrpc import FD

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('expression')
args = parser.parse_args()

client = gravelrpc.Client(args.name)
print eval('client.' + args.expression)
