from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from plenum.common.constants import TXN_AUTHOR_AGREEMENT_VERSION
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.static_taa_helper import StaticTAAHelper
from plenum.server.request_handlers.txn_author_agreement_handler import TxnAuthorAgreementHandler \
    as PTxnAuthorAgreementHandler


class TxnAuthorAgreementHandler(PTxnAuthorAgreementHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager)
        self.write_req_validator = write_req_validator

    def authorize(self, request):
        version = request.operation.get(TXN_AUTHOR_AGREEMENT_VERSION)
        if StaticTAAHelper.get_taa_digest(self.state, version, isCommitted=False) is None:
            self.write_req_validator.validate(request,
                                              [AuthActionAdd(txn_type=self.txn_type,
                                                             field='*',
                                                             value='*')])
        else:
            self.write_req_validator.validate(request,
                                              [AuthActionEdit(txn_type=self.txn_type,
                                                              field='*',
                                                              old_value='*',
                                                              new_value='*')])
