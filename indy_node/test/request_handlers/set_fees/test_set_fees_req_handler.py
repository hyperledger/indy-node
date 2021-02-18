import pytest

from indy_common.constants import FEE
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


def test_update_state(set_fees_handler, get_fees_handler, get_fee_handler,
                      set_fees_request, get_fees_request, get_fee_request,
                      fee_value, valid_fees):
    txn = reqToTxn(set_fees_request)

    set_fees_handler.update_state(txn, None, set_fees_request, is_committed=True)
    fees_map = get_fees_handler.get_fees(get_fees_request)

    assert fees_map == valid_fees
