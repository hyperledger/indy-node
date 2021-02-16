import pytest
from plenum.common.constants import DATA
from plenum.common.exceptions import RequestRejectedException
from plenum.test.freeze_ledgers.helper import sdk_get_frozen_ledgers, sdk_send_freeze_ledgers
from plenum.test.helper import freshness

FRESHNESS_TIMEOUT = 5


@pytest.fixture(scope="module")
def tconf(tconf):
    with freshness(tconf, enabled=True, timeout=FRESHNESS_TIMEOUT):
        yield tconf


def test_send_freeze_ledgers(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_trustee_list):
    with pytest.raises(RequestRejectedException, match="Not enough TRUSTEE signatures"):
        sdk_send_freeze_ledgers(
            looper, sdk_pool_handle,
            sdk_wallet_trustee_list[:-1],
            []
        )

    # check that the config state doesn't contain frozen ledgers records
    result = sdk_get_frozen_ledgers(looper, sdk_pool_handle,
                                    sdk_wallet_trustee_list[0])[1]["result"][DATA]
    assert result is None

    # add to the config state a frozen ledgers record with an empty list
    sdk_send_freeze_ledgers(
        looper, sdk_pool_handle,
        sdk_wallet_trustee_list,
        []
    )

    # check that the config state contains a frozen ledgers record with an empty list
    result = sdk_get_frozen_ledgers(looper, sdk_pool_handle,
                                    sdk_wallet_trustee_list[0])[1]["result"][DATA]
    assert len(result) == 0
