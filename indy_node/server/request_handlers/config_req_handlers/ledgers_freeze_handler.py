from typing import Optional

from indy_common.authorize.auth_actions import AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from plenum.common.constants import LEDGERS_FREEZE
from plenum.common.request import Request
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.ledgers_freeze.ledgers_freeze_handler import LedgersFreezeHandler as PLedgersFreezeHandler


class LedgersFreezeHandler(PLedgersFreezeHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager)
        self.write_req_validator = write_req_validator

    def authorize(self, request):
        self.write_req_validator.validate(request,
                                          [AuthActionEdit(txn_type=LEDGERS_FREEZE,
                                                          field='*',
                                                          old_value='*',
                                                          new_value='*')])
