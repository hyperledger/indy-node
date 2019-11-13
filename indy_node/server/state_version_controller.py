from indy_common.constants import NODE_UPGRADE, ACTION, COMPLETE
from plenum.common.constants import VERSION
from plenum.common.txn_util import get_type, get_payload_data


class StateVersionController:

    def __init__(self) -> None:
        self._version = None

    @property
    def version(self):
        return self._version

    def update_version(self, txn):
        if get_type(txn) == NODE_UPGRADE and get_payload_data(txn)[ACTION] == COMPLETE:
            self._version = get_payload_data(txn)[VERSION]

