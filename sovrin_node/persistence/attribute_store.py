from plenum.persistence.kv_store import KVStoreLeveldb


class AttributeStore:
    """
    Stores attributes as key value pair where the key is hash of the
    attribute as stored in ledger and value is the actual value if the attribute
    """

    def __init__(self, dbPath):
        self.dbPath = dbPath
        self.db = KVStoreLeveldb(dbPath)

    def set(self, key, value):
        self.db.set(key, value)

    def get(self, key):
        val = self.db.get(key)
        return val.decode()

    def remove(self, key):
        self.db.remove(key)

    def close(self):
        self.db.close()
