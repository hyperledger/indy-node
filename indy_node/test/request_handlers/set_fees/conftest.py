import pytest

from indy_common.constants import FEES_ALIAS, GET_FEE, GET_FEES, SET_FEES, FEES
from indy_node.server.request_handlers.config_req_handlers.fees.set_fees_handler import SetFeesHandler
from indy_node.server.request_handlers.read_req_handlers.get_fee_handler import GetFeeHandler
from indy_node.server.request_handlers.read_req_handlers.get_fees_handler import GetFeesHandler
from plenum.common.constants import TXN_TYPE

from plenum.common.request import Request


@pytest.fixture(scope="function")
def txn_alias():
    return "txn_alias1"


@pytest.fixture(scope="function")
def fee_value():
    return 1


@pytest.fixture(scope="function")
def valid_fees(txn_alias, fee_value):
    return {
        txn_alias: fee_value,
        "alias2": 2
    }


@pytest.fixture(scope="function")
def get_fee_request(creator, txn_alias):
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
def set_fees_request(creator, valid_fees):
    return Request(identifier=creator,
                   signature="signature",
                   operation={TXN_TYPE: SET_FEES,
                              FEES: valid_fees})


@pytest.fixture
def set_fees_handler(db_manager, write_auth_req_validator):
    return SetFeesHandler(db_manager, write_auth_req_validator)


@pytest.fixture
def get_fee_handler(db_manager):
    return GetFeeHandler(db_manager)


@pytest.fixture
def get_fees_handler(db_manager):
    return GetFeesHandler(db_manager)
