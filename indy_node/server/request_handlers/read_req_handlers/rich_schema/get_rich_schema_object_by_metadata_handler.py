from indy_common.constants import RS_NAME, GET_RICH_SCHEMA_OBJECT_BY_METADATA, \
    RS_TYPE, RS_VERSION
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.abstract_rich_schema_object_handler import \
    AbstractRichSchemaObjectHandler
from indy_node.server.request_handlers.read_req_handlers.rich_schema.abstract_rich_schema_read_req_handler import \
    AbstractRichSchemaReadRequestHandler
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager


class GetRichSchemaObjectByMetadataHandler(AbstractRichSchemaReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_RICH_SCHEMA_OBJECT_BY_METADATA, DOMAIN_LEDGER_ID)

    def get_result(self, request: Request):
        super().get_result(request)
        self._validate_request_type(request)

        secondary_key = AbstractRichSchemaObjectHandler.make_secondary_key(request.operation[RS_TYPE],
                                                                           request.operation[RS_NAME],
                                                                           request.operation[RS_VERSION])
        value, seq_no, last_update_time, proof = None, None, None, None
        try:
            id, proof = self._get_value_from_state(secondary_key, with_proof=True)
            if id is not None:
                value, seq_no, last_update_time, proof = self.lookup(id, is_committed=True, with_proof=True)
        except KeyError:
            # means absence of data
            pass

        return self.make_result(request=request,
                                data=value,
                                last_seq_no=seq_no,
                                update_time=last_update_time,
                                proof=proof)
