from typing import Any, Optional, Tuple, Union
from indy_common.constants import GET_NYM, TIMESTAMP, NYM_VERSION

from common.serializers.serialization import domain_state_serializer
from indy_node.server.request_handlers.domain_req_handlers.nym_handler import NymHandler
from indy_node.server.request_handlers.utils import StateValue
from plenum.common.constants import TARGET_NYM, TXN_TIME, DOMAIN_LEDGER_ID, TXN_METADATA_SEQ_NO
from plenum.common.request import Request
from plenum.common.types import f
from plenum.common.txn_util import get_txn_time
from plenum.common.exceptions import InvalidClientRequest
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler


class GetNymHandler(ReadRequestHandler):
    def __init__(self, node, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_NYM, DOMAIN_LEDGER_ID)
        self.node = node

    def get_result(self, request: Request):
        self._validate_request_type(request)
        nym = request.operation[TARGET_NYM]
        path = NymHandler.make_state_path_for_nym(nym)
        timestamp = self._retrieve_timestamp(request)

        data = None
        seq_no = None
        update_time = None
        proof = None

        nym_data, proof = self._get_value_at_timestamp_from_state(
            path, timestamp=timestamp, with_proof=True
        )
        if nym_data:
            nym_data = domain_state_serializer.deserialize(nym_data)
            nym_data[TARGET_NYM] = nym
            data = domain_state_serializer.serialize(nym_data)
            seq_no = nym_data[f.SEQ_NO.nm]
            update_time = nym_data[TXN_TIME]

        result = self.make_result(
            request=request,
            data=data,  # Serailized retrieved txn data
            last_seq_no=seq_no,  # nym_data[seqNo]
            update_time=update_time,  # nym_data[TXN_TIME]
            proof=proof,  # _get_value_from_state(..., with_proof=True)[1]
        )

        result.update(request.operation)
        return result

    def _get_value_at_timestamp_from_state(
        self, path: bytes, timestamp: Optional[str], with_proof=False
    ) -> Tuple[Optional[Union[bytes, str]], Any]:
        """Return the value and proof at a time in the past or None if it didn't exist.

        If timestamp is none, return current state.
        """
        past_root = None
        if timestamp:
            past_root = self.database_manager.ts_store.get_equal_or_prev(timestamp)

        return self._get_value_from_state(
            path, head_hash=past_root, with_proof=with_proof
        )

    def _retrieve_timestamp(self, request: Request):
        timestamp = request.operation.get(TIMESTAMP, None)
        read_seq_no = request.operation.get("seqNo", None)
        if timestamp and read_seq_no:
            raise InvalidClientRequest(
                request.identifier,
                request.reqId,
                "Cannot resolve nym with both seqNo and timestamp present.",
            )
        elif read_seq_no:
            db = self.database_manager.get_database(DOMAIN_LEDGER_ID)
            txn = self.node.getReplyFromLedger(db.ledger, read_seq_no, write=False)
            if txn and "result" in txn:
                timestamp = get_txn_time(txn.result)
        return timestamp
