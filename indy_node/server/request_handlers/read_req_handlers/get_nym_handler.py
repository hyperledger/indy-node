from indy_common.constants import GET_NYM, TIMESTAMP

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

        if timestamp:
            nym_data = None
            past_root = self.database_manager.ts_store.get_equal_or_prev(timestamp)
            if past_root:
                encoded_nym, proof = self._get_value_from_state(
                    path, head_hash=past_root, with_proof=True
                )
                if encoded_nym:
                    nym_data = domain_state_serializer.deserialize(encoded_nym)
                    seq_no = nym_data[TXN_METADATA_SEQ_NO]
                    update_time = nym_data[TXN_TIME]
                    del nym_data[TXN_METADATA_SEQ_NO]
                    del nym_data[TXN_TIME]
                    del nym_data["identifier"]
            nym_state_value = StateValue(
                root_hash=past_root,
                value=nym_data,
                seq_no=seq_no,
                update_time=update_time,
                proof=proof,
            )
            if nym_state_value and nym_state_value.value:
                nym_data = nym_state_value.value
                nym_data[TARGET_NYM] = nym
                data = domain_state_serializer.serialize(nym_data)
                seq_no = nym_state_value.seq_no
                update_time = nym_state_value.update_time
                proof = nym_state_value.proof
        else:
            nym_data, proof = self._get_value_from_state(path, with_proof=True)
            if nym_data:
                nym_data = domain_state_serializer.deserialize(nym_data)
                nym_data[TARGET_NYM] = nym
                data = domain_state_serializer.serialize(nym_data)
                seq_no = nym_data[f.SEQ_NO.nm]
                update_time = nym_data[TXN_TIME]

        result = self.make_result(
            request=request,
            data=data,
            last_seq_no=seq_no,
            update_time=update_time,
            proof=proof,
        )

        result.update(request.operation)
        return result

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
