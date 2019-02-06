from indy_common.constants import GET_NYM

from common.serializers.serialization import domain_state_serializer
from indy_common.state import domain

from plenum.common.constants import TARGET_NYM, TXN_TIME, DOMAIN_LEDGER_ID
from plenum.common.request import Request
from plenum.common.types import f
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler


class GetNymHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_NYM, DOMAIN_LEDGER_ID)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        nym = request.operation[TARGET_NYM]
        path = domain.make_state_path_for_nym(nym)
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

        # TODO: add update time here!
        result = self.make_result(request=request,
                                  data=data,
                                  last_seq_no=seq_no,
                                  update_time=update_time,
                                  proof=proof)

        result.update(request.operation)
        return result
