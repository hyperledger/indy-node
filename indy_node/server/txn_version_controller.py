from indy_common.constants import NODE_UPGRADE, ACTION, COMPLETE, POOL_UPGRADE, START, SCHEDULE
from plenum.common.constants import VERSION, DATA
from plenum.common.txn_util import get_type, get_payload_data, get_from, get_txn_time
from plenum.common.util import SortedDict
from plenum.server.txn_version_controller import TxnVersionController as TVController


class TxnVersionController(TVController):

    def __init__(self) -> None:
        self._versions = SortedDict()
        self._f = 0
        self._votes_for_new_version = SortedDict()

    @property
    def version(self):
        return self._versions.peekitem(-1)[1] if self._versions else None

    def get_pool_version(self, timestamp):
        if timestamp is None:
            return self.version
        last_version = None
        for upgrade_tm, version in self._versions.items():
            if timestamp < upgrade_tm:
                return last_version
            last_version = version
        return last_version

    def update_version(self, txn):
        if get_type(txn) == POOL_UPGRADE and get_payload_data(txn).get(ACTION) == START:
            N = len(get_payload_data(txn).get(SCHEDULE, {}))
            self._f = (N - 1) // 3
        elif get_type(txn) == NODE_UPGRADE and get_payload_data(txn)[DATA][ACTION] == COMPLETE:
            version = get_payload_data(txn)[DATA][VERSION]
            self._votes_for_new_version.setdefault(version, set())
            self._votes_for_new_version[version].add(get_from(txn))
            if len(self._votes_for_new_version[version]) > self._f:
                self._versions[get_txn_time(txn)] = version
                self._votes_for_new_version = SortedDict({v: senders
                                                          for v, senders in self._votes_for_new_version.items()
                                                          if v > version})
