import json

import pytest
from plenum.common.constants import TXN_TYPE, DATA
from plenum.test.freshness.helper import check_freshness_updated_for_ledger

from plenum.test.helper import sdk_sign_and_submit_op, sdk_get_and_check_replies, freshness

from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.config import SCHEMA_ATTRIBUTES_LIMIT
from indy_common.constants import SCHEMA_NAME, SCHEMA_VERSION, SCHEMA_ATTR_NAMES, DOMAIN_LEDGER_ID, LEDGERS_IDS, \
    LEDGERS_FREEZE, GET_FROZEN_LEDGERS
from indy_common.types import SchemaField
from indy_node.test.api.helper import validate_write_reply, sdk_write_schema_and_check
from indy_node.test.freeze_ledgers.helper import sdk_send_freeze_ledgers, sdk_get_frozen_ledgers
from plenum.common.exceptions import RequestRejectedException, RequestNackedException
from plenum.common.util import randomString
from plenum.config import NAME_FIELD_LIMIT
from stp_core.loop.eventually import eventually

FRESHNESS_TIMEOUT = 5


@pytest.fixture(scope="module")
def tconf(tconf):
    with freshness(tconf, enabled=True, timeout=FRESHNESS_TIMEOUT):
        yield tconf



def test_send_freeze_ledgers(looper, txnPoolNodeSet, sdk_pool_handle, sdk_wallet_trustee,
                             sdk_wallet_trustee_list):
    ledger_to_remove = DOMAIN_LEDGER_ID

    looper.run(eventually(
        check_freshness_updated_for_ledger, txnPoolNodeSet, ledger_to_remove,
        timeout=3 * FRESHNESS_TIMEOUT)
    )
    # op = {TXN_TYPE: "123",
    #       LEDGERS_IDS: [DOMAIN_LEDGER_ID]}
    # req = sdk_sign_and_submit_op(looper, sdk_pool_handle, sdk_wallet_trustee, op)
    # sdk_get_and_check_replies(looper, [req])
    #

    # op = {TXN_TYPE: "124"}
    # req = sdk_sign_and_submit_op(looper, sdk_pool_handle, sdk_wallet_trustee, op)
    # result = sdk_get_and_check_replies(looper, [req])
    sdk_send_freeze_ledgers(
        looper, sdk_pool_handle,
        sdk_wallet_trustee_list,
        [ledger_to_remove]
    )



    result = sdk_get_frozen_ledgers(looper, sdk_pool_handle,
                                    sdk_wallet_trustee)[1]["result"][DATA]
    print(result)

    assert result[ledger_to_remove]["state"]
    assert result[ledger_to_remove]["ledger"]
    assert result[ledger_to_remove]["ledger"] >= 0
