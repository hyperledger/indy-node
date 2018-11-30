import json
import pytest

from indy.ledger import build_pool_config_request

from indy_node.test.nym_txn.test_nym_additional import get_nym
from indy_node.test.upgrade.helper import sdk_ensure_upgrade_sent
from indy_node.test.pool_config.helper import sdk_ensure_pool_config_sent

from plenum.common.exceptions import RequestNackedException
from plenum.common.types import OPERATION
from plenum.test.helper import sdk_get_bad_response, sdk_sign_and_submit_req
from plenum.common.constants import VERSION
from plenum.test.pool_transactions.helper import sdk_add_new_nym

from indy_node.test.upgrade.conftest import validUpgrade, nodeIds


def sdk_pool_bad_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee, change_writes,
                             change_force, change_writes_value=None, change_force_value=None):
    _, did = sdk_wallet_trustee
    req = looper.loop.run_until_complete(build_pool_config_request(
        did, True, True))
    req = json.loads(req)
    del req[OPERATION]['writes']
    req[OPERATION][change_writes] = change_writes_value if change_writes_value else True
    del req[OPERATION]['force']
    req[OPERATION][change_force] = change_force_value if change_force_value else True
    req = json.dumps(req)
    req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, req)
    return req


def testPoolConfigInvalidSyntax(looper, sdk_pool_handle, sdk_wallet_trustee, poolConfigWTFF):
    req = sdk_pool_bad_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                                   'wites', 'force', True, False)
    sdk_get_bad_response(looper, [req], RequestNackedException, 'missed fields - writes')
    req = sdk_pool_bad_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                                   'writes', 'force', 'Tue', False)
    sdk_get_bad_response(looper, [req], RequestNackedException, 'expected types \'bool\', got \'str\'')
    req = sdk_pool_bad_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                                   'writes', 'force', True, 1)
    sdk_get_bad_response(looper, [req], RequestNackedException, 'expected types \'bool\', got \'int\'')


def testPoolConfigWritableFalse(looper, sdk_pool_handle, sdk_wallet_trustee, poolConfigWFFF):
    sdk_ensure_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                                poolConfigWFFF)
    with pytest.raises(RequestNackedException) as e:
        sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee)
    e.match('Pool is in readonly mode')


def testPoolConfigWritableTrue(looper, sdk_pool_handle, sdk_wallet_trustee, poolConfigWTFF):
    with pytest.raises(RequestNackedException) as e:
        sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee)
    e.match('Pool is in readonly mode')
    sdk_ensure_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                                poolConfigWTFF)
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee)


def testPoolConfigWritableFalseCanRead(looper, sdk_pool_handle, sdk_wallet_trustee, poolConfigWFFF):
    _, did = sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee)
    get_nym(looper, sdk_pool_handle, sdk_wallet_trustee, did)
    sdk_ensure_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                                poolConfigWFFF)
    with pytest.raises(RequestNackedException) as e:
        sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee)
    e.match('Pool is in readonly mode')
    get_nym(looper, sdk_pool_handle, sdk_wallet_trustee, did)


def testPoolUpgradeOnReadonlyPool(
        looper, nodeSet, sdk_pool_handle, sdk_wallet_trustee, validUpgrade, poolConfigWFFF):
    sdk_ensure_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                                poolConfigWFFF)
    sdk_ensure_upgrade_sent(looper, sdk_pool_handle, sdk_wallet_trustee,
                     validUpgrade)

    for node in nodeSet:
        assert len(node.upgrader.aqStash) > 0
        assert node.upgrader.scheduledAction
        assert node.upgrader.scheduledAction[0] == validUpgrade[VERSION]
