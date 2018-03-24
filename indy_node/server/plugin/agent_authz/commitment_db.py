from storage.kv_store import KeyValueStorage


# Db to store commitments of an add only accumulator
class CommitmentDb:
    # TODO: A better option would be to rely on the sorted nature of key
    # storage and have keys like `comm:<comm>idx:<i>`. That way its just one kind of key
    SIZE_KEY_NAME = '__size__'
    IDX_KEY_PREFIX = 'i:'
    COMM_KEY_PREFIX = 'c:'

    def __init__(self, kv_store: KeyValueStorage):
        self.kv_store = kv_store
        try:
            self.kv_store.get(self.SIZE_KEY_NAME)
        except KeyError:
            self.kv_store.put(self.SIZE_KEY_NAME, b'0')

    def add_commitment(self, commitment):
        new_index = str(self.size + 1)
        batch = [
            (self.commitment_key(commitment), new_index),
            (self.index_key(new_index), commitment),
            (self.SIZE_KEY_NAME, new_index)
        ]
        self.kv_store.setBatch(batch)

    def has_commitment(self, commitment):
        try:
            self.kv_store.get(self.commitment_key(commitment))
            return True
        except KeyError:
            return False

    def get_commitment_index(self, commitment):
        return int(self.kv_store.get(self.commitment_key(commitment)))

    def all_commitments_from_index(self, index):
        commitments = []
        to = self.size
        for i in range(index, to+1):
            try:
                commitments.append(self.kv_store.get(self.index_key(i)).decode())
            except KeyError:
                break
        return commitments

    @property
    def size(self):
        return int(self.kv_store.get(self.SIZE_KEY_NAME))

    @staticmethod
    def commitment_key(commitment):
        return '{}{}'.format(CommitmentDb.COMM_KEY_PREFIX, commitment)

    @staticmethod
    def index_key(index):
        return '{}{}'.format(CommitmentDb.IDX_KEY_PREFIX, index)
