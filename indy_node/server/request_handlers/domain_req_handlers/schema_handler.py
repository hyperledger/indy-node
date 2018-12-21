from indy_common.state import domain

from indy_common.roles import Roles

from indy_common.auth import Authoriser

from indy_common.constants import SCHEMA

from indy_common.req_utils import get_write_schema_name, get_write_schema_version
from indy_node.server.request_handlers.read_req_handlers.get_schema_handler import GetSchemaHandler
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest, UnknownIdentifier, UnauthorizedClientRequest

from plenum.common.request import Request
from plenum.common.txn_util import get_type
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class SchemaHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager, get_schema_handler: GetSchemaHandler):
        super().__init__(database_manager, SCHEMA, DOMAIN_LEDGER_ID)
        self.get_schema_handler = get_schema_handler

    def static_validation(self, request: Request):
        pass

    def dynamic_validation(self, request: Request):
        # we can not add a Schema with already existent NAME and VERSION
        # sine a Schema needs to be identified by seqNo
        identifier = request.identifier
        schema_name = get_write_schema_name(request)
        schema_version = get_write_schema_version(request)
        schema, _, _, _ = self.get_schema_handler.getSchema(
            author=identifier,
            schemaName=schema_name,
            schemaVersion=schema_version,
            with_proof=False)
        if schema:
            raise InvalidClientRequest(identifier, request.reqId,
                                       '{} can have one and only one SCHEMA with '
                                       'name {} and version {}'
                                       .format(identifier, schema_name, schema_version))
        try:
            origin_role = self.idrCache.getRole(
                request.identifier, isCommitted=False) or None
        except BaseException:
            raise UnknownIdentifier(
                request.identifier,
                request.reqId)
        r, msg = Authoriser.authorised(typ=SCHEMA,
                                       actorRole=origin_role)
        if not r:
            raise UnauthorizedClientRequest(
                request.identifier,
                request.reqId,
                "{} cannot add schema".format(
                    Roles.nameFromValue(origin_role))
            )

    def gen_txn_path(self, txn):
        path = domain.prepare_schema_for_state(txn, path_only=True)
        return path.decode()

    def _updateStateWithSingleTxn(self, txn, isCommitted=False) -> None:
        assert get_type(txn) == SCHEMA
        path, value_bytes = domain.prepare_schema_for_state(txn)
        self.state.set(path, value_bytes)

    @property
    def idrCache(self):
        return self.database_manager.get_store('idr')
