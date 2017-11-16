from storage.kv_store import KeyValueStorage


class AttributeStore:
    """
    Stores attributes as key value pair where the key is hash of the
    attribute as stored in ledger and value is the actual value if the attribute
    """

    def __init__(self, keyValueStorage: KeyValueStorage):
        self._keyValueStorage = keyValueStorage

    def set(self, key, value):
        self._keyValueStorage.put(key, value)

    def get(self, key):
        val = self._keyValueStorage.get(key)
        return val.decode()

    def remove(self, key):
        self._keyValueStorage.remove(key)

    def close(self):
        self._keyValueStorage.close()
