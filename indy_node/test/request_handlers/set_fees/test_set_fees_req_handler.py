import pytest

from indy_node.server.request_handlers.config_req_handlers.fees.fees_static_helper import FeesStaticHelper
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.txn_util import reqToTxn


def test_static_validation_missing_fees(set_fees_request, set_fees_handler):
    """
    StaticValidation of a set fees request fails because it's forbidden.
    """
    with pytest.raises(InvalidClientRequest, match="SET_FEES transactions are forbidden now."):
        set_fees_handler.static_validation(set_fees_request)


def test_dynamic_validation_invalid_signee(set_fees_request, set_fees_handler):
    """
    Validation of a set fees request fails because it's forbidden.
    """
    with pytest.raises(InvalidClientRequest, match="SET_FEES transactions are forbidden now."):
        set_fees_handler.dynamic_validation(set_fees_request, None)


def test_update_state(set_fees_handler, set_fees_request, config_state, txn_alias, fee_value, valid_fees):
    txn = reqToTxn(set_fees_request)

    set_fees_handler.update_state(txn, None, set_fees_request, is_committed=True)
    fees_map = FeesStaticHelper.get_fee_from_state(config_state)
    state_fee_value = FeesStaticHelper.get_fee_from_state(config_state, txn_alias)

    assert state_fee_value == fee_value
    assert fees_map == valid_fees
