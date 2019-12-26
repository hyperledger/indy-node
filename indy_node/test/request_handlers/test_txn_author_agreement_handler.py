import pytest as pytest

from common.serializers.serialization import domain_state_serializer, config_state_serializer
from indy_node.server.request_handlers.config_req_handlers.txn_author_agreement_handler import TxnAuthorAgreementHandler
from indy_node.test.request_handlers.helper import get_exception, add_to_idr
from plenum.common.constants import ROLE, STEWARD, NYM, TARGET_NYM, TXN_TYPE, TXN_AUTHOR_AGREEMENT, \
    TXN_AUTHOR_AGREEMENT_TEXT, TXN_AUTHOR_AGREEMENT_VERSION, TRUSTEE, DOMAIN_LEDGER_ID
from plenum.common.exceptions import UnauthorizedClientRequest, InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data, reqToTxn, get_reply_nym
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.static_taa_helper import StaticTAAHelper
from plenum.server.request_handlers.utils import get_nym_details, get_role, is_steward, nym_to_state_key, \
    encode_state_value
from plenum.test.testing_utils import FakeSomething


@pytest.fixture(scope="module")
def txn_author_agreement_handler(db_manager, write_auth_req_validator):
    handler = TxnAuthorAgreementHandler(db_manager, write_auth_req_validator)
    return handler


@pytest.fixture(scope="module")
def set_aml(txn_author_agreement_handler):
    txn_author_agreement_handler.state.set(StaticTAAHelper.state_path_taa_aml_latest(),
                                           encode_state_value("value", "seqNo", "txnTime",
                                                              serializer=config_state_serializer))


def test_dynamic_validation_without_permission(taa_request,
                                               txn_author_agreement_handler: TxnAuthorAgreementHandler,
                                               creator,
                                               set_aml):
    add_to_idr(txn_author_agreement_handler.database_manager.idr_cache, creator, STEWARD)
    with pytest.raises(UnauthorizedClientRequest, match="Not enough TRUSTEE signatures"):
        txn_author_agreement_handler.dynamic_validation(taa_request, 0)


def test_dynamic_validation(taa_request,
                            txn_author_agreement_handler: TxnAuthorAgreementHandler,
                            creator,
                            set_aml):
    add_to_idr(txn_author_agreement_handler.database_manager.idr_cache, creator, TRUSTEE)
    txn_author_agreement_handler.dynamic_validation(taa_request, 0)

