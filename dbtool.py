#!/usr/bin/env python
import sys
import graveldb

def help():
    sys.exit('''usage:
    dbtool.py filename
    dbtool.py filename key
    dbtool.py filename key property val
    dbtool.py filename key --del''')

if len(sys.argv) not in (2, 3, 4, 5):
    help()

db = graveldb.TDB_BSON_Shelf(sys.argv[1])

if len(sys.argv) == 2:
    print db.keys()
elif len(sys.argv) == 3:
    print db[sys.argv[2]]
elif len(sys.argv) == 4:
    if sys.argv[3] == '--del':
        del db[sys.argv[2]]
    else:
        help()
elif len(sys.argv) == 5:
    val = db[sys.argv[2]]
    setattr(val, sys.argv[3], eval(sys.argv[4]))
    db[sys.argv[2]] = val
