import pytest
from indy_common.constants import FEES_ALIAS
from indy_node.server.request_handlers.read_req_handlers.get_fee_handler import GetFeeHandler
from plenum.common.exceptions import InvalidClientRequest


@pytest.fixture
def get_fee_handler(db_manager):
    return GetFeeHandler(db_manager)


def test_get_fee_valid_alias(get_fee_request, get_fee_handler):
    """
    StaticValidation of a get fee request with all of the whitelisted txn
    types.
    """
    result = get_fee_handler.static_validation(get_fee_request)
    assert result is None
