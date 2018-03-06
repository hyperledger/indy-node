import logging
import warnings

from stp_core.common.log import Logger

from plenum.common.util import randomString
from plenum.test import waits as plenumWaits
from plenum.test.helper import waitForSufficientRepliesForRequests
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
    ALIAS, SERVICES, VALIDATOR, STEWARD, BLS_KEY

from indy_client.test.helper import getClientAddedWithRole

# noinspection PyUnresolvedReferences
from indy_client.test.conftest import trustAnchorWallet, \
    trustAnchor, tdirWithDomainTxnsUpdated, updatedDomainTxnFile, \
    stewardWallet, steward, genesisTxns, testClientClass, client_ledger_dir, \
    addedTrustAnchor, userWalletB, nodeSet, testNodeClass, updatedPoolTxnData, \
    trusteeData, trusteeWallet, trustee, warnfilters as client_warnfilters

# noinspection PyUnresolvedReferences
from plenum.test.conftest import tdir, client_tdir, nodeReg, up, ready, \
    whitelist, concerningLogLevels, logcapture, keySharedNodes, \
    startedNodes, tdirWithPoolTxns, tdirWithDomainTxns, tdirWithClientPoolTxns, txnPoolNodeSet, \
    poolTxnData, dirName, poolTxnNodeNames, allPluginsPath, tdirWithNodeKeepInited, \
    poolTxnStewardData, poolTxnStewardNames, getValueFromModule, \
    patchPluginManager, txnPoolNodesLooper, warncheck, \
    warnfilters as plenum_warnfilters, do_post_node_creation

# noinspection PyUnresolvedReferences
from indy_common.test.conftest import general_conf_tdir, tconf, poolTxnTrusteeNames, \
    domainTxnOrderedFields, looper, setTestLogLevel, node_config_helper_class, config_helper_class

from plenum.test.conftest import sdk_pool_handle, sdk_pool_name, sdk_wallet_steward, sdk_wallet_handle, \
    sdk_wallet_name, sdk_steward_seed, sdk_wallet_client


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


@pytest.fixture("module")
def nodeThetaAdded(looper, nodeSet, tdirWithClientPoolTxns,
                   tconf, steward, stewardWallet, allPluginsPath, testNodeClass,
                   testClientClass, node_config_helper_class, tdir, node_name='Theta'):
    newStewardName = "testClientSteward" + randomString(3)
    newNodeName = node_name
    newSteward, newStewardWallet = getClientAddedWithRole(nodeSet,
                                                          tdirWithClientPoolTxns,
                                                          looper, steward,
                                                          stewardWallet,
                                                          newStewardName,
                                                          role=STEWARD)

    sigseed = randomString(32).encode()
    nodeSigner = SimpleSigner(seed=sigseed)

    (nodeIp, nodePort), (clientIp, clientPort) = genHa(2)

    config_helper = node_config_helper_class(newNodeName, tconf, chroot=tdir)

    _, _, bls_key = initNodeKeysForBothStacks(
        newNodeName, config_helper.keys_dir, sigseed, override=True)

    data = {
        NODE_IP: nodeIp,
        NODE_PORT: nodePort,
        CLIENT_IP: clientIp,
        CLIENT_PORT: clientPort,
        ALIAS: newNodeName,
        SERVICES: [VALIDATOR, ],
        BLS_KEY: bls_key
    }

    node = Node(nodeSigner.identifier, data, newStewardWallet.defaultId)

    newStewardWallet.addNode(node)
    reqs = newStewardWallet.preparePending()
    req = newSteward.submitReqs(*reqs)[0][0]

    waitForSufficientRepliesForRequests(looper, newSteward, requests=[req])

    def chk():
        assert newStewardWallet.getNode(node.id).seqNo is not None

    timeout = plenumWaits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(chk, retryWait=1, timeout=timeout))

    newNode = testNodeClass(newNodeName,
                            config_helper=config_helper,
                            config=tconf,
                            ha=(nodeIp, nodePort), cliha=(
                                clientIp, clientPort),
                            pluginPaths=allPluginsPath)

    nodeSet.append(newNode)
    looper.add(newNode)
    looper.run(checkNodesConnected(nodeSet))
    ensureClientConnectedToNodesAndPoolLedgerSame(looper, steward,
                                                  *nodeSet)
    ensureClientConnectedToNodesAndPoolLedgerSame(looper, newSteward,
                                                  *nodeSet)
    return newSteward, newStewardWallet, newNode
