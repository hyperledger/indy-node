from typing import Optional

from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator

from indy_common.constants import SET_CONTEXT, META, CONTEXT_CONTEXT

from indy_common.req_utils import get_write_context_name, get_write_context_version, get_txn_context_name, \
    get_txn_context_version, get_txn_context_data, get_txn_context_meta
from indy_common.state.state_constants import MARKER_CONTEXT
from plenum.common.constants import DOMAIN_LEDGER_ID, DATA
from plenum.common.exceptions import InvalidClientRequest

from plenum.common.request import Request
from plenum.common.txn_util import get_request_data, get_from, get_seq_no, get_txn_time
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler
from plenum.server.request_handlers.utils import encode_state_value

from re import findall

URI_REGEX = r'^(?P<scheme>\w+):(?:(?:(?P<url>//[.\w]+)(?:(/(?P<path>[/\w]+)?)?))|(?:(?P<method>\w+):(?P<id>\w+)))'


class ContextHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager, SET_CONTEXT, DOMAIN_LEDGER_ID)
        self.write_req_validator = write_req_validator

    def static_validation(self, request: Request):
        self._validate_request_type(request)
        data = request.operation[DATA]
        self._validate_context(data[CONTEXT_CONTEXT], request.identifier, request.reqId)

    def dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        # we can not add a Context with already existent NAME and VERSION
        # since a Context needs to be identified by seqNo
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)
        context_name = get_write_context_name(request)
        context_version = get_write_context_version(request)
        path = ContextHandler.make_state_path_for_context(identifier, context_name, context_version)
        context, _, _ = self.get_from_state(path)
        if context:
            self.write_req_validator.validate(request,
                                              [AuthActionEdit(txn_type=SET_CONTEXT,
                                                              field='*',
                                                              old_value='*',
                                                              new_value='*')])
        else:
            self.write_req_validator.validate(request,
                                              [AuthActionAdd(txn_type=SET_CONTEXT,
                                                             field='*',
                                                             value='*')])

    def gen_txn_id(self, txn):
        self._validate_txn_type(txn)
        path = ContextHandler.prepare_context_for_state(txn, path_only=True)
        return path.decode()

    def update_state(self, txn, prev_result, request, is_committed=False) -> None:
        self._validate_txn_type(txn)
        path, value_bytes = ContextHandler.prepare_context_for_state(txn)
        self.state.set(path, value_bytes)

    def _validate_context(self, context, id, reqId):
        if isinstance(context, list):
            for ctx in context:
                if not isinstance(ctx, dict):
                    if self._bad_uri(ctx):
                        raise InvalidClientRequest(id, reqId, '@context URI {} badly formed'.format(ctx))
        elif isinstance(context, dict):
            pass
        elif isinstance(context, str):
            if self._bad_uri(context):
                raise InvalidClientRequest(id, reqId, '@context URI {} badly formed'.format(context))
        else:
            raise InvalidClientRequest(id, reqId, "'@context' value must be url, array, or object")

    def _bad_uri(self, uri_string):
        url = findall(URI_REGEX, uri_string)
        if not url:
            return True
        return False

    @staticmethod
    def make_state_path_for_context(authors_did, context_name, context_version) -> bytes:
        return "{DID}:{MARKER}:{CONTEXT_NAME}:{CONTEXT_VERSION}" \
            .format(DID=authors_did,
                    MARKER=MARKER_CONTEXT,
                    CONTEXT_NAME=context_name,
                    CONTEXT_VERSION=context_version).encode()

    @staticmethod
    def prepare_context_for_state(txn, path_only=False):
        origin = get_from(txn)
        context_name = get_txn_context_name(txn)
        context_version = get_txn_context_version(txn)
        value = {
            META: get_txn_context_meta(txn),
            DATA: get_txn_context_data(txn)
        }
        path = ContextHandler.make_state_path_for_context(origin, context_name, context_version)
        if path_only:
            return path
        seq_no = get_seq_no(txn)
        txn_time = get_txn_time(txn)
        value_bytes = encode_state_value(value, seq_no, txn_time)
        return path, value_bytes
