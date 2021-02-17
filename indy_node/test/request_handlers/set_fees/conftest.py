import pytest

from indy_common.constants import FEES_ALIAS, GET_FEE, GET_FEES, SET_FEES, FEES
from indy_node.server.request_handlers.config_req_handlers.fees.set_fees_handler import SetFeesHandler
from plenum.common.constants import TXN_TYPE

from plenum.common.request import Request

txn_alias = "txn_alias1"
fees_value = 1
VALID_FEES = {
    txn_alias: fees_value,
}


@pytest.fixture(scope="function")
def get_fee_request(creator):
    return Request(identifier=creator,
                   signature="signature",
                   operation={TXN_TYPE: GET_FEE,
                              FEES_ALIAS: txn_alias})


@pytest.fixture(scope="function")
def get_fees_request(creator):
    return Request(identifier=creator,
                   signature="signature",
                   operation={TXN_TYPE: GET_FEES})


@pytest.fixture(scope="function")
def set_fees_request(creator):
    return Request(identifier=creator,
                   signature="signature",
                   operation={TXN_TYPE: SET_FEES,
                              FEES: VALID_FEES})


@pytest.fixture
def set_fees_handler(db_manager, write_auth_req_validator):
    return SetFeesHandler(db_manager, write_auth_req_validator)
