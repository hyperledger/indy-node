from stp_core.common.log import getlogger
from storage.kv_store_leveldb_int_keys import KeyValueStorageLeveldbIntKeys

logger = getlogger()


class StateTsDbStorage():
    def __init__(self, name, storage):
        logger.debug("Initializing timestamp-root_hash storage for revocation")
        self._storage = storage
        self._name = name

    def __repr__(self):
        return self._name

    def get(self, timestamp: int):
        value = self._storage.get(str(timestamp))
        return value

    def set(self, timestamp: int, root_hash: bytes):
        self._storage.put(str(timestamp), root_hash)

    def close(self):
        self._storage.close()

    def get_equal_or_prev(self, timestamp):
        # return value can be:
        #    None, if required key less then minimal key from DB
        #    Equal by key if key exist in DB
        #    Previous if key does not exist in Db, but there is key less than required

        try:
            value = self.get(timestamp)
        except KeyError:
            prev_value = None
            for k, v in self._storage.iterator():
                if int(k) > timestamp:
                    break
                prev_value = v
            value = prev_value
        return value
