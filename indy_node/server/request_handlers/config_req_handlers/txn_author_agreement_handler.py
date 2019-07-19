from indy_common.authorize.auth_actions import AuthActionAdd
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.txn_author_agreement_handler import TxnAuthorAgreementHandler \
    as PTxnAuthorAgreementHandler


class TxnAuthorAgreementHandler(PTxnAuthorAgreementHandler):

    def __init__(self, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(database_manager)
        self.write_req_validator = write_req_validator

    def authorize(self, request):
        self.write_req_validator.validate(request,
                                          [AuthActionAdd(txn_type=self.txn_type,
                                                         field='*',
                                                         value='*')])
