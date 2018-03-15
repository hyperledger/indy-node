from stp_core.common.log import getlogger

logger = getlogger()


class StateTsDbStorage():
    def __init__(self, name, storage):
        logger.debug("Initializing timestamp-rootHash storage")
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
        return self._storage.get_equal_or_prev(str(timestamp))
