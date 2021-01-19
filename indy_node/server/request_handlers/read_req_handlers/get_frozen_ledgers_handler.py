from common.serializers.serialization import domain_state_serializer
from indy_common.authorize.auth_constraints import ConstraintsSerializer
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.state import config
from indy_common.types import ClientGetAuthRuleOperation
from indy_node.server.request_handlers.config_req_handlers.auth_rule.abstract_auth_rule_handler import \
    AbstractAuthRuleHandler
from indy_node.server.request_handlers.config_req_handlers.auth_rule.static_auth_rule_helper import StaticAuthRuleHelper
from indy_node.server.request_handlers.config_req_handlers.ledger_freeze_handler import LedgerFreezeHandler
from plenum.common.txn_util import get_request_data
from plenum.server.request_handlers.handler_interfaces.read_request_handler import ReadRequestHandler

from indy_common.authorize.auth_actions import EDIT_PREFIX, split_action_id
from indy_common.constants import CONFIG_LEDGER_ID, AUTH_ACTION, OLD_VALUE, \
    NEW_VALUE, AUTH_TYPE, FIELD, CONSTRAINT, GET_AUTH_RULE, GET_FROZEN_LEDGERS
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager


class GetFrozenLedgersHandler(ReadRequestHandler):

    def __init__(self, database_manager: DatabaseManager):
        super().__init__(database_manager, GET_FROZEN_LEDGERS, CONFIG_LEDGER_ID)

    def static_validation(self, request: Request):
        self._validate_request_type(request)

    def get_result(self, request: Request):
        self._validate_request_type(request)
        state_path = LedgerFreezeHandler.make_state_path_for_frozen_ledgers()
        try:
            data, last_seq_no, last_update_time, proof = self.lookup(state_path, is_committed=True, with_proof=True)
        except KeyError:
            data, last_seq_no, last_update_time, proof = None, None, None, None
        result = self.make_result(request=request,
                                  data=data,
                                  last_seq_no=last_seq_no,
                                  update_time=last_update_time,
                                  proof=proof)
        return result

