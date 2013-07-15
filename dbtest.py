import graveldb

class Screw(graveldb.Table('Screw', '/tmp')):
    default = lambda self: graveldb.Object(size=1)

s = Screw('foo')
with s:
    s.data.size += 1
    s.save()

s = Screw('foo')
print s.data.size
