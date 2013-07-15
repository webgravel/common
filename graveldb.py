import shelve
import tdb
import os

class TDBShelf(shelve.Shelf):
    def __init__(self, path):
        self.db = tdb.open(path, flags=os.O_RDWR | os.O_CREAT)
        shelve.Shelf.__init__(self, self.db)

    def lock_all(self):
        self.db.lock_all()

    def unlock_all(self):
        self.db.unlock_all()

def Table(name, path):
    return type(name, (_Table,), {'table': TDBShelf(path + '/' + name)})

class _Table(object):
    def __init__(self, name):
        self.name = name
        self.data = self.table.get(name, self.default())

    def save(self):
        self.table[self.name] = self.data

    def __enter__(self):
        self.table.lock_all()

    def __exit__(self, *args):
        self.table.unlock_all()

    default = lambda self: Object()

class Object(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)