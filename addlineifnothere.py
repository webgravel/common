#!/usr/bin/env python
import sys

if len(sys.argv) != 3:
    sys.exit('Usage: addlineifnothere filename line')

fn = sys.argv[1]
line = sys.argv[2]

if line not in open(fn).read().splitlines():
    with open(fn, 'a') as f:
        f.write('\n%s\n' % line)
