import leveldb

from plenum.persistence.util import removeLockFiles


class AttributeStore:
    """
    Stores attributes as key value pair where the key is hash of the
    attribute as stored in ledger and value is the actual value if the attribute
    """

    def __init__(self, dbPath):
        self.dbPath = dbPath
        self.db = leveldb.LevelDB(dbPath)

    def set(self, key, value):
        if not isinstance(key, str):
            key = key.encode()
        if not isinstance(value, str):
            value = value.encode()
        self.db.Put(key, value)

    def get(self, key):
        if not isinstance(key, str):
            key = key.encode()
        val = self.db.Get(key)
        return val.decode()

    def remove(self, key):
        if not isinstance(key, str):
            key = key.encode()
        self.db.Delete(key)

    def close(self):
        removeLockFiles(self.dbPath)
        del self._db
        self._db = None