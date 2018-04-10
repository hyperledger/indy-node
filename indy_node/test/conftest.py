import logging
import warnings

from plenum.test.pool_transactions.helper import sdk_add_new_nym, sdk_pool_refresh, prepare_new_node_data, \
    create_and_start_new_node, prepare_node_request, sdk_sign_and_send_prepared_request
from stp_core.common.log import Logger

from plenum.common.util import randomString
from plenum.test import waits as plenumWaits
from plenum.test.helper import waitForSufficientRepliesForRequests, sdk_get_and_check_replies
from plenum.test.node_catchup.helper import \
    ensureClientConnectedToNodesAndPoolLedgerSame
from plenum.test.test_node import checkNodesConnected
from stp_core.loop.eventually import eventually
from stp_core.network.port_dispenser import genHa

from indy_client.client.wallet.node import Node
from indy_common import strict_types

# typecheck during tests
strict_types.defaultShouldCheck = True

import pytest

from plenum.common.signer_simple import SimpleSigner
from plenum.common.keygen_utils import initNodeKeysForBothStacks, init_bls_keys
from plenum.common.constants import NODE_IP, NODE_PORT, CLIENT_IP, CLIENT_PORT, \
    ALIAS, SERVICES, VALIDATOR, STEWARD, BLS_KEY, STEWARD_STRING

from indy_client.test.helper import getClientAddedWithRole

# noinspection PyUnresolvedReferences
from indy_client.test.conftest import trustAnchorWallet, \
    trustAnchor, tdirWithDomainTxnsUpdated, updatedDomainTxnFile, \
    stewardWallet, steward, genesisTxns, testClientClass, client_ledger_dir, \
    addedTrustAnchor, userWalletB, nodeSet, testNodeClass, updatedPoolTxnData, \
    trusteeData, trusteeWallet, trustee, warnfilters as client_warnfilters

# noinspection PyUnresolvedReferences
from plenum.test.conftest import tdir, client_tdir, nodeReg, \
    whitelist, concerningLogLevels, logcapture, \
    tdirWithPoolTxns, tdirWithDomainTxns, tdirWithClientPoolTxns, txnPoolNodeSet, \
    poolTxnData, dirName, poolTxnNodeNames, allPluginsPath, tdirWithNodeKeepInited, \
    poolTxnStewardData, poolTxnStewardNames, getValueFromModule, \
    patchPluginManager, txnPoolNodesLooper, warncheck, \
    warnfilters as plenum_warnfilters, do_post_node_creation

# noinspection PyUnresolvedReferences
from indy_common.test.conftest import general_conf_tdir, tconf, poolTxnTrusteeNames, \
    domainTxnOrderedFields, looper, setTestLogLevel, node_config_helper_class, config_helper_class

from plenum.test.conftest import sdk_pool_handle, sdk_pool_name, sdk_wallet_steward, sdk_wallet_handle, \
    sdk_wallet_name, sdk_steward_seed, sdk_wallet_client, sdk_wallet_trustee, sdk_trustee_seed, trustee_data, \
    sdk_client_seed, poolTxnClientData, poolTxnClientNames

Logger.setLogLevel(logging.NOTSET)


@pytest.fixture(scope="session")
def warnfilters(client_warnfilters):
    def _():
        client_warnfilters()
        warnings.filterwarnings(
            'ignore',
            category=DeprecationWarning,
            module='indy_common\.persistence\.identity_graph',
            message="The 'warn' method is deprecated")
        warnings.filterwarnings(
            'ignore', category=ResourceWarning, message='unclosed transport')

    return _


@pytest.fixture(scope='module')
def sdk_node_theta_added(looper,
                         txnPoolNodeSet,
                         tdir,
                         tconf,
                         sdk_pool_handle,
                         sdk_wallet_trustee,
                         allPluginsPath,
                         node_config_helper_class,
                         testNodeClass,
                         name=None):
    new_steward_name = "testClientSteward" + randomString(3)
    new_node_name = name or "Theta"

    new_steward_wallet = sdk_add_new_nym(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         alias=new_steward_name,
                                         role=STEWARD_STRING)

    sigseed, verkey, bls_key, nodeIp, nodePort, clientIp, clientPort = \
        prepare_new_node_data(tconf, tdir, new_node_name,
                              configClass=node_config_helper_class)

    # filling node request
    _, steward_did = new_steward_wallet
    node_request = looper.loop.run_until_complete(
        prepare_node_request(steward_did,
                             new_node_name=new_node_name,
                             clientIp=clientIp,
                             clientPort=clientPort,
                             nodeIp=nodeIp,
                             nodePort=nodePort,
                             bls_key=bls_key,
                             sigseed=sigseed,
                             services=[VALIDATOR]))

    # sending request using 'sdk_' functions
    request_couple = sdk_sign_and_send_prepared_request(looper, new_steward_wallet,
                                                        sdk_pool_handle, node_request)

    # waitng for replies
    sdk_get_and_check_replies(looper, [request_couple])

    new_node = create_and_start_new_node(looper, new_node_name, tdir, sigseed,
                                         (nodeIp, nodePort), (clientIp, clientPort),
                                         tconf, True, allPluginsPath,
                                         testNodeClass,
                                         configClass=node_config_helper_class)

    txnPoolNodeSet.append(new_node)
    looper.run(checkNodesConnected(txnPoolNodeSet))
    sdk_pool_refresh(looper, sdk_pool_handle)
    return new_steward_wallet, new_node
