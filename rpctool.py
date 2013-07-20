#!/usr/bin/env python
import argparse
import gravelrpc

parser = argparse.ArgumentParser()
parser.add_argument('name')
parser.add_argument('expression')
args = parser.parse_args()

client = gravelrpc.Client(args.name)
print eval('client.' + args.expression)
