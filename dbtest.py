import graveldb

class Screw(graveldb.Table('Screw', '/tmp')):
    default = dict(size=1)

s = Screw('foo')
with s:
    s.data.size += 1
    s.save()

s = Screw('foo')
print s.data.size
