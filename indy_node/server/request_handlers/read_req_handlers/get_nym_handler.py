from indy_common.constants import GET_NYM, TIMESTAMP, VALUE

from common.serializers.serialization import domain_state_serializer
from indy_node.server.request_handlers.domain_req_handlers.nym_handler import NymHandler
from indy_node.server.request_handlers.utils import StateValue
from plenum.common.constants import TARGET_NYM, TXN_TIME, DOMAIN_LEDGER_ID, TXN_METADATA_SEQ_NO
from plenum.common.request import Request
from plenum.common.types import f
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler
from plenum.server.request_handlers.utils import decode_state_value


class GetNymHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_NYM, DOMAIN_LEDGER_ID)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        nym = request.operation[TARGET_NYM]
        timestamp = request.operation.get(TIMESTAMP, None)
        path = NymHandler.make_state_path_for_nym(nym)
        # Get old state based on timestamp. See https://hyperledger.github.io/indy-did-method/#did-versions
        if timestamp:
            nym_state_value = self._get_nym_by_timestamp(timestamp, path)
            if nym_state_value:
                nym_data = nym_state_value.value
                nym_data[TARGET_NYM] = nym
                data = domain_state_serializer.serialize(nym_data)
                seq_no = nym_state_value.seq_no
                update_time = nym_state_value.update_time
                proof = nym_state_value.proof
            # Can't find state for timestamp
            else:
                data = None
                seq_no = None,
                update_time = None
                proof = None
        else:
            # Get current state
            nym_data, proof = self._get_value_from_state(path, with_proof=True)
            if nym_data:
                nym_data = domain_state_serializer.deserialize(nym_data)
                nym_data[TARGET_NYM] = nym
                data = domain_state_serializer.serialize(nym_data)
                seq_no = nym_data[f.SEQ_NO.nm]
                update_time = nym_data[TXN_TIME]
            else:
                data = None
                seq_no = None
                update_time = None

        result = self.make_result(
            request=request,
            data=data,
            last_seq_no=seq_no,
            update_time=update_time,
            proof=proof,
        )

        result.update(request.operation)
        return result

    def _get_nym_by_timestamp(self, timestamp, path_to_nym):
        nym_data = None
        seq_no = None
        last_update_time = None
        nym_data_proof = None
        past_root = self.database_manager.ts_store.get_equal_or_prev(timestamp)
        if past_root:
            encoded_nym, nym_data_proof = self._get_value_from_state(
                path_to_nym, head_hash=past_root, with_proof=True
            )
            if encoded_nym:
                nym_data = domain_state_serializer.deserialize(encoded_nym)
                seq_no = nym_data[TXN_METADATA_SEQ_NO]
                last_update_time = nym_data[TXN_TIME]
                del nym_data[TXN_METADATA_SEQ_NO]
                del nym_data[TXN_TIME]
                del nym_data["identifier"]
        return StateValue(
            root_hash=past_root,
            value=nym_data,
            seq_no=seq_no,
            update_time=last_update_time,
            proof=nym_data_proof,
        )
