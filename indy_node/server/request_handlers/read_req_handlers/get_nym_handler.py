from indy_common.constants import GET_NYM, VERSION_ID, VERSION_TIME

from common.serializers.serialization import domain_state_serializer
from indy_node.server.request_handlers.domain_req_handlers.nym_handler import NymHandler
from plenum.common.constants import TARGET_NYM, TXN_TIME, DOMAIN_LEDGER_ID
from plenum.common.request import Request
from plenum.common.types import f
from plenum.common.exceptions import InvalidClientRequest
from plenum.server.database_manager import DatabaseManager

from .version_read_request_handler import VersionReadRequestHandler


class GetNymHandler(VersionReadRequestHandler):
    def __init__(self, node, database_manager: DatabaseManager):
        super().__init__(node, database_manager, GET_NYM, DOMAIN_LEDGER_ID)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        nym = request.operation[TARGET_NYM]
        path = NymHandler.make_state_path_for_nym(nym)

        timestamp = request.operation.get(VERSION_TIME)
        seq_no = request.operation.get(VERSION_ID)

        if timestamp and seq_no:
            raise InvalidClientRequest(
                request.identifier,
                request.reqId,
                f"{VERSION_ID} and {VERSION_TIME} are mutually exclusive; only one should be "
                "specified",
            )
        # The above check determines whether the request is valid
        # A similar check in VersionReadRequestHandler determines
        # whether the method is used correctly

        data = None
        last_seq_no = None
        update_time = None
        proof = None

        nym_data, proof = self.lookup_version(
            path, seq_no=seq_no, timestamp=timestamp, with_proof=True
        )

        if nym_data:
            nym_data = domain_state_serializer.deserialize(nym_data)
            nym_data[TARGET_NYM] = nym
            data = domain_state_serializer.serialize(nym_data)
            last_seq_no = nym_data[f.SEQ_NO.nm]
            update_time = nym_data[TXN_TIME]

        result = self.make_result(
            request=request,
            data=data,  # Serailized retrieved txn data
            last_seq_no=last_seq_no,  # nym_data[seqNo]
            update_time=update_time,  # nym_data[TXN_TIME]
            proof=proof,  # _get_value_from_state(..., with_proof=True)[1]
        )

        result.update(request.operation)
        return result
