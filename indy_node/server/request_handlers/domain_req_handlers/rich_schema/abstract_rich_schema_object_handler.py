from abc import ABCMeta, abstractmethod
from typing import Optional

from common.serializers.json_serializer import JsonSerializer
from indy_common.authorize.auth_actions import AuthActionEdit, AuthActionAdd
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.constants import DOMAIN_LEDGER_ID, RS_ID, RS_TYPE, RS_VERSION, RS_NAME, RS_CONTENT, JSON_LD_ID_FIELD, \
    JSON_LD_TYPE_FIELD
from indy_common.state.domain import encode_state_value
from indy_common.types import Request
from plenum.common.constants import TXN_PAYLOAD_METADATA_ENDORSER, TXN_PAYLOAD_METADATA_FROM, TXN_PAYLOAD_VERSION
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.txn_util import get_payload_data, get_seq_no, get_txn_time, get_from, get_endorser, \
    get_payload_txn_version
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class AbstractRichSchemaObjectHandler(WriteRequestHandler, metaclass=ABCMeta):

    def __init__(self, txn_type, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager, txn_type, DOMAIN_LEDGER_ID)
        self.write_req_validator = write_req_validator

    @abstractmethod
    def is_json_ld_content(self):
        pass

    @abstractmethod
    def do_static_validation_content(self, content_as_dict, request):
        pass

    @abstractmethod
    def do_dynamic_validation_content(self, request):
        pass

    def static_validation(self, request: Request):
        self._validate_request_type(request)
        try:
            content_as_dict = JsonSerializer.loads(request.operation[RS_CONTENT])
        except ValueError:
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "'{}' must be a JSON serialized string".format(RS_CONTENT))

        if self.is_json_ld_content():
            self.do_static_validation_json_ld(content_as_dict, request)

        self.do_static_validation_content(content_as_dict, request)

    def do_static_validation_json_ld(self, content_as_dict, request):
        if not content_as_dict.get(JSON_LD_ID_FIELD):
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "'content' must be a valid JSON-LD and have non-empty '{}' field".format(JSON_LD_ID_FIELD))
        if not content_as_dict.get(JSON_LD_TYPE_FIELD):
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "'content' must be a valid JSON-LD and have non-empty '{}' field".format(
                                           JSON_LD_TYPE_FIELD))

        if content_as_dict[JSON_LD_ID_FIELD] != request.operation[RS_ID]:
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       "content's @id must be equal to id={}".format(request.operation[RS_ID]))

    def dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        self._validate_request_type(request)

        rs_id = request.operation[RS_ID]
        rs_object, _, _ = self.get_from_state(rs_id)

        # check that (rs_name, rs_type, rs_version) is unique within all rich schema objects
        secondary_key = self.make_secondary_key(request.operation[RS_TYPE],
                                                request.operation[RS_NAME],
                                                request.operation[RS_VERSION])
        if not rs_object and self.state.get(secondary_key, isCommitted=False) is not None:
            raise InvalidClientRequest(request.identifier,
                                       request.reqId,
                                       'An object with {rs_name}="{rs_name_value}", {rs_version}="{rs_version_value}" '
                                       'and {rs_type}="{rs_type_value}" already exists. '
                                       'Please choose different {rs_name}, {rs_version} or {rs_type}'.format(
                                           rs_name=RS_NAME, rs_version=RS_VERSION, rs_type=RS_TYPE,
                                           rs_name_value=request.operation[RS_NAME],
                                           rs_version_value=request.operation[RS_VERSION],
                                           rs_type_value=request.operation[RS_TYPE]))

        # do common auth-rule-based validation (which will check the default immutability of most of the objects)
        if rs_object:
            self.write_req_validator.validate(request,
                                              [AuthActionEdit(txn_type=self.txn_type,
                                                              field='*',
                                                              old_value='*',
                                                              new_value='*')])
        else:
            self.write_req_validator.validate(request,
                                              [AuthActionAdd(txn_type=self.txn_type,
                                                             field='*',
                                                             value='*')])

        self.do_dynamic_validation_content(request)

    def update_state(self, txn, prev_result, request, is_committed=False) -> None:
        self._validate_txn_type(txn)

        txn_data = get_payload_data(txn)

        primary_key = txn_data[RS_ID].encode()
        secondary_key = self.make_secondary_key(txn_data[RS_TYPE],
                                                txn_data[RS_NAME],
                                                txn_data[RS_VERSION])

        value = {
            RS_ID: txn_data[RS_ID],
            RS_TYPE: txn_data[RS_TYPE],
            RS_NAME: txn_data[RS_NAME],
            RS_VERSION: txn_data[RS_VERSION],
            RS_CONTENT: txn_data[RS_CONTENT],
            TXN_PAYLOAD_METADATA_FROM: get_from(txn),
            TXN_PAYLOAD_METADATA_ENDORSER: get_endorser(txn),
            TXN_PAYLOAD_VERSION: get_payload_txn_version(txn),
        }
        seq_no = get_seq_no(txn)
        txn_time = get_txn_time(txn)
        value_bytes = encode_state_value(value, seq_no, txn_time)

        self.state.set(primary_key, value_bytes)
        self.state.set(secondary_key, primary_key)

    def gen_txn_id(self, txn):
        self._validate_txn_type(txn)
        return get_payload_data(txn)[RS_ID]

    @staticmethod
    def make_secondary_key(rs_type, rs_name, rs_version):
        return "{RS_TYPE}:{RS_NAME}:{RS_VERSION}".format(RS_TYPE=rs_type,
                                                         RS_NAME=rs_name,
                                                         RS_VERSION=rs_version).encode()
