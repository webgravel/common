import tdb
import bson
import os

from bson.binary import Binary

class TDBShelf(object):
    def __init__(self, path):
        self.db = tdb.open(path, flags=os.O_RDWR | os.O_CREAT)

    def __getitem__(self, name):
        return self._unpickle(self.db[_mkkey(name)])

    def __setitem__(self, name, val):
        self.db[_mkkey(name)] = self._pickle(val)

    def __delitem__(self, name):
        del self.db[_mkkey(name)]

    def close(self):
        self.db.close()

    def __del__(self):
        self.close()

    def lock_all(self):
        self.db.lock_all()

    def unlock_all(self):
        self.db.unlock_all()

    def keys(self):
        return list(self.db.iterkeys())

    def __enter__(self):
        self.lock_all()

    def __exit__(self, type, value, tb):
        self.unlock_all()
        if type:
            raise

def _mkkey(k):
    if isinstance(k, (str, int)):
        return str(k)
    elif isinstance(k, unicode):
        return k.encode('utf8')
    else:
        raise TypeError('expected str or int')

class TDB_BSON_Shelf(TDBShelf):
    def _pickle(self, val):
        return bson.BSON.encode(val.__dict__)

    def _unpickle(self, val):
        decoded = bson.BSON(val).decode()
        return Object(**decoded)

def Table(name, path):
    return type(name, (_Table,), {'table': TDB_BSON_Shelf(path + '/' + name)})

class _Table(object):
    __slots__ = ('data', 'name', 'exists')
    autocreate = True

    def __init__(self, name, autocreate=None):
        self.name = name
        if autocreate is None:
            autocreate = self.autocreate
        try:
            self.data = self.table[name]
            self.exists = True
        except KeyError:
            if not autocreate:
                raise
            self.data = Object()
            self.exists = False
        self._setup()

    def _setup(self):
        for k, v in self.default.items():
            if not hasattr(self.data, k):
                setattr(self.data, k, v)
        self.setup()
        self.validate()

    def setup(self):
        pass

    def validate(self):
        pass

    def save(self):
        self.validate()
        self.table[self.name] = self.data

    @classmethod
    def all(cls):
        return map(cls, cls.table.keys())

    def __enter__(self):
        return self.table.__enter__()

    def __exit__(self, type, value, tb):
        return self.table.__exit__(type, value, tb)

    def __repr__(self):
        return '<%s %s: %r>' % (self.__class__.__name__, self.name, self.data.__dict__)

    default = {}

class Object(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return '<Object %s>' % self.__dict__

class RaceConditionError(Exception):
    pass
