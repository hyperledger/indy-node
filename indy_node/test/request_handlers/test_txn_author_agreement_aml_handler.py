import pytest as pytest

from common.serializers.serialization import domain_state_serializer
from indy_node.server.request_handlers.config_req_handlers.txn_author_agreement_aml_handler import \
    TxnAuthorAgreementAmlHandler
from indy_node.test.request_handlers.helper import get_exception, add_to_idr
from plenum.common.constants import ROLE, STEWARD, NYM, TARGET_NYM, TXN_TYPE, TXN_AUTHOR_AGREEMENT, \
    TXN_AUTHOR_AGREEMENT_TEXT, TXN_AUTHOR_AGREEMENT_VERSION, TRUSTEE, DOMAIN_LEDGER_ID, TXN_AUTHOR_AGREEMENT_AML, \
    AML_VERSION, AML, AML_CONTEXT
from plenum.common.exceptions import UnauthorizedClientRequest
from plenum.common.request import Request
from plenum.test.testing_utils import FakeSomething


@pytest.fixture(scope="module")
def txn_author_agreement_aml_handler(db_manager, write_auth_req_validator):
    handler = TxnAuthorAgreementAmlHandler(db_manager, write_auth_req_validator)
    return handler


@pytest.fixture(scope="module")
def aml_request(txn_author_agreement_aml_handler, creator):
    return Request(identifier=creator,
                   signature="signature",
                   operation={TXN_TYPE: TXN_AUTHOR_AGREEMENT_AML,
                              AML_VERSION: "AML_VERSION",
                              AML: {"test": "test"},
                              AML_CONTEXT: "AML_CONTEXT"})


def test_dynamic_validation_without_permission(aml_request,
                                               txn_author_agreement_aml_handler: TxnAuthorAgreementAmlHandler,
                                               creator):
    add_to_idr(txn_author_agreement_aml_handler.database_manager.idr_cache, creator, STEWARD)
    with pytest.raises(UnauthorizedClientRequest, match="Not enough TRUSTEE signatures"):
        txn_author_agreement_aml_handler.dynamic_validation(aml_request)


def test_dynamic_validation(aml_request,
                            txn_author_agreement_aml_handler: TxnAuthorAgreementAmlHandler,
                            creator):
    add_to_idr(txn_author_agreement_aml_handler.database_manager.idr_cache, creator, TRUSTEE)
    txn_author_agreement_aml_handler.dynamic_validation(aml_request)
