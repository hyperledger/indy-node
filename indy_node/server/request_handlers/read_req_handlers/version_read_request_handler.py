
from typing import Any, Optional, Tuple, Union, cast
from plenum.common.txn_util import get_txn_time
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler
from plenum.server.node import Node
from storage.state_ts_store import StateTsDbStorage


class VersionReadRequestHandler(ReadRequestHandler):
    """Specialized read request handler enabling looking up past versions."""

    def __init__(
        self, node: Node, database_manager: DatabaseManager, txn_type, ledger_id
    ):
        super().__init__(database_manager, txn_type, ledger_id)
        self.node = node
        self.timestamp_store: StateTsDbStorage = cast(
            StateTsDbStorage, self.database_manager.ts_store
        )

    def lookup_version(
        self,
        path: bytes,
        seq_no: Optional[int] = None,
        timestamp: Optional[int] = None,
        with_proof=False,
    ) -> Tuple[Optional[Union[bytes, str]], Any]:
        """Lookup a value from the ledger state, optionally retrieving from the past.

        If seq_no or timestamp is specified and no value is found, returns (None, None).
        If neither are specified, value in its current state is retrieved, which will
        also return (None, None) if it is not found on the ledger.

        seq_no and timestamp are mutually exclusive.
        """
        if seq_no is not None and timestamp is not None:
            raise ValueError("seq_no and timestamp are mutually exclusive")
        # The above check determines whether the method is used correctly
        # A similar check in GetNymHandler and GetAttributeHandler determines
        # whether the request is valid

        if seq_no:
            timestamp = self._timestamp_from_seq_no(seq_no)
            if not timestamp:
                return None, None

        if timestamp:
            past_root = self.timestamp_store.get_equal_or_prev(timestamp, ledger_id=self.ledger_id)
            if past_root:
                return self._get_value_from_state(
                    path, head_hash=past_root, with_proof=with_proof
                )

            return None, None

        return self._get_value_from_state(
            path, with_proof=with_proof
        )

    def _timestamp_from_seq_no(self, seq_no: int) -> Optional[int]:
        """Return timestamp of a transaction identified by seq_no."""
        db = self.database_manager.get_database(self.ledger_id)
        txn = self.node.getReplyFromLedger(db.ledger, seq_no, write=False)

        if txn and "result" in txn:
            return get_txn_time(txn.result)
        return None
