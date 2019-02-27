from plenum.common.constants import RAW, ENC, HASH


class StateValue:
    def __init__(self, root_hash=None, value=None, seq_no=None, update_time=None, proof=None):
        self.root_hash = root_hash
        self.value = value
        self.seq_no = seq_no
        self.update_time = update_time
        self.proof = proof


def validate_attrib_keys(operation):
    data_keys = {RAW, ENC, HASH}.intersection(set(operation.keys()))
    return len(data_keys) == 1
