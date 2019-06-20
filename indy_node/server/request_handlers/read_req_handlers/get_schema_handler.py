from indy_common.constants import SCHEMA_NAME, SCHEMA_VERSION, GET_SCHEMA
from indy_common.req_utils import get_read_schema_from, get_read_schema_name, get_read_schema_version
from indy_node.server.request_handlers.domain_req_handlers.schema_handler import SchemaHandler
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler


class GetSchemaHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_SCHEMA, DOMAIN_LEDGER_ID)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        author_did = get_read_schema_from(request)
        schema_name = get_read_schema_name(request)
        schema_version = get_read_schema_version(request)
        schema, last_seq_no, last_update_time, proof = self.get_schema(
            author=author_did,
            schema_name=schema_name,
            schema_version=schema_version,
            with_proof=True
        )
        # TODO: we have to do this since SCHEMA has a bit different format than other txns
        # (it has NAME and VERSION inside DATA, and it's not part of the state value, but state key)
        if schema is None:
            schema = {}
        schema.update({
            SCHEMA_NAME: schema_name,
            SCHEMA_VERSION: schema_version
        })
        return self.make_result(request=request,
                                data=schema,
                                last_seq_no=last_seq_no,
                                update_time=last_update_time,
                                proof=proof)

    def get_schema(self,
                   author: str,
                   schema_name: str,
                   schema_version: str,
                   is_committed=True,
                   with_proof=True) -> (str, int, int, list):
        assert author is not None
        assert schema_name is not None
        assert schema_version is not None
        path = SchemaHandler.make_state_path_for_schema(author, schema_name, schema_version)
        try:
            keys, seq_no, last_update_time, proof = self.lookup(path, is_committed, with_proof=with_proof)
            return keys, seq_no, last_update_time, proof
        except KeyError:
            return None, None, None, None
