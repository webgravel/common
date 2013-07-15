#!/usr/bin/env python
import sys
import graveldb

if len(sys.argv) not in (2, 3, 5):
    sys.exit('usage: dbtool.py filename [key [property val]]')

db = graveldb.TDBShelf(sys.argv[1])

if len(sys.argv) == 2:
    print list(db.iterkeys())
elif len(sys.argv) == 3:
    print db[sys.argv[2]]
elif len(sys.argv) == 5:
    val = db[sys.argv[2]]
    setattr(val, sys.argv[3], eval(sys.argv[4]))
    db[sys.argv[2]] = val
