from copy import deepcopy

from plenum.common.constants import NAME, VERSION, STEWARD_STRING
from plenum.common.exceptions import RequestNackedException, RequestRejectedException
from indy_common.constants import CANCEL, \
    ACTION
from indy_node.test.upgrade.helper import bumpedVersion, sdk_send_upgrade
from plenum.test.helper import sdk_get_bad_response

whitelist = ['Failed to upgrade node']


def testNodeRejectsPoolUpgrade(looper, nodeSet, tdir, sdk_pool_handle,
                               sdk_wallet_trustee, invalidUpgrade):
    req = sdk_send_upgrade(looper, sdk_pool_handle, sdk_wallet_trustee, invalidUpgrade)
    sdk_get_bad_response(looper, [req], RequestNackedException, 'since time span between upgrades')


def testOnlyTrusteeCanSendPoolUpgrade(looper, sdk_pool_handle, sdk_wallet_steward, validUpgrade):
    # A steward sending POOL_UPGRADE but txn fails
    validUpgrade = deepcopy(validUpgrade)
    validUpgrade[NAME] = 'upgrade-20'
    validUpgrade[VERSION] = bumpedVersion(validUpgrade['version'])
    req = sdk_send_upgrade(looper, sdk_pool_handle, sdk_wallet_steward, validUpgrade)
    sdk_get_bad_response(looper, [req], RequestRejectedException, '{} can not do this action'.format(STEWARD_STRING))


def testNonTrustyCannotCancelUpgrade(looper, validUpgradeSent, sdk_pool_handle,
                                     sdk_wallet_steward, validUpgrade):
    validUpgradeCopy = deepcopy(validUpgrade)
    validUpgradeCopy[ACTION] = CANCEL
    req = sdk_send_upgrade(looper, sdk_pool_handle, sdk_wallet_steward, validUpgradeCopy)
    sdk_get_bad_response(looper, [req], RequestRejectedException, '{} can not do this action'.format(STEWARD_STRING))


def test_accept_then_reject_upgrade(
        looper, sdk_pool_handle, sdk_wallet_trustee, validUpgradeSent, validUpgrade):
    upgrade_name = validUpgrade[NAME]
    error_msg = "InvalidClientRequest(\"Upgrade '{}' is already scheduled\"". \
        format(upgrade_name)

    validUpgrade2 = deepcopy(validUpgrade)

    req = sdk_send_upgrade(looper, sdk_pool_handle, sdk_wallet_trustee, validUpgrade2)
    sdk_get_bad_response(looper, [req], RequestRejectedException, error_msg)


def testOnlyTrusteeCanSendPoolUpgradeForceTrue(
        looper, sdk_pool_handle, sdk_wallet_steward, validUpgradeExpForceTrue):
    req = sdk_send_upgrade(looper, sdk_pool_handle, sdk_wallet_steward, validUpgradeExpForceTrue)
    sdk_get_bad_response(looper, [req], RequestNackedException, '{} can not do this action'.format(STEWARD_STRING))
