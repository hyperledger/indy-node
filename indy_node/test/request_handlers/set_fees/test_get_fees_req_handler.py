import pytest

from indy_node.server.request_handlers.read_req_handlers.get_fees_handler import GetFeesHandler


@pytest.fixture
def get_fees_handler(db_manager):
    return GetFeesHandler(db_manager)


def test_get_fees(get_fees_request, get_fees_handler):
    """
    StaticValidation of a get fees request does nothing.
    """
    get_fees_handler.static_validation(get_fees_request)
