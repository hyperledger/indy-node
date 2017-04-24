import warnings

from plenum.common.keygen_utils import initLocalKeys
from plenum.common.util import randomString
from plenum.test import waits as plenumWaits
from plenum.test.helper import waitForSufficientRepliesForRequests
from plenum.test.node_catchup.helper import \
    ensureClientConnectedToNodesAndPoolLedgerSame
from plenum.test.test_node import checkNodesConnected
from stp_core.loop.eventually import eventually
from stp_core.network.port_dispenser import genHa

from sovrin_client.client.wallet.node import Node
from sovrin_common import strict_types

# typecheck during tests
strict_types.defaultShouldCheck = True

import pytest

from plenum.common.signer_simple import SimpleSigner
from plenum.common.constants import NODE_IP, NODE_PORT, CLIENT_IP, CLIENT_PORT, \
    ALIAS, SERVICES, VALIDATOR, STEWARD, TXN_ID, TRUSTEE, TYPE

from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.constants import NYM, TARGET_NYM, ROLE

from sovrin_node.test.helper import TestNode, \
    buildStewardClient

from sovrin_client.test.helper import addRole, getClientAddedWithRole

# noinspection PyUnresolvedReferences
from sovrin_client.test.conftest import trustAnchorWallet, \
    trustAnchor, tdirWithDomainTxnsUpdated, updatedDomainTxnFile, trusteeData,\
    trusteeWallet, stewardWallet, steward, genesisTxns, testClientClass, \
    addedTrustAnchor, userIdA, userIdB, userClientA, userClientB, nodeSet, \
    testNodeClass, warnfilters as client_warnfilters

# noinspection PyUnresolvedReferences
from plenum.test.conftest import tdir, nodeReg, up, ready, \
    whitelist, concerningLogLevels, logcapture, keySharedNodes, \
    startedNodes, tdirWithDomainTxns, txnPoolNodeSet, poolTxnData, dirName, \
    poolTxnNodeNames, allPluginsPath, tdirWithNodeKeepInited, tdirWithPoolTxns, \
    poolTxnStewardData, poolTxnStewardNames, getValueFromModule, \
    nodeAndClientInfoFilePath, patchPluginManager, txnPoolNodesLooper, \
    warncheck, warnfilters as plenum_warnfilters

# noinspection PyUnresolvedReferences
from sovrin_common.test.conftest import conf, tconf, poolTxnTrusteeNames, \
    domainTxnOrderedFields, looper


@pytest.fixture(scope="session")
def warnfilters(client_warnfilters):
    def _():
        client_warnfilters()
        warnings.filterwarnings('ignore', category=DeprecationWarning, module='sovrin_common\.persistence\.identity_graph', message="The 'warn' method is deprecated")
        warnings.filterwarnings('ignore', category=ResourceWarning, message='unclosed transport')
    return _


@pytest.fixture(scope="module")
def updatedPoolTxnData(poolTxnData):
    data = poolTxnData
    trusteeSeed = 'thisistrusteeseednotsteward12345'
    signer = SimpleSigner(seed=trusteeSeed.encode())
    t = {
        TARGET_NYM: signer.verkey,
        ROLE: TRUSTEE,
        TYPE: NYM,
        ALIAS: "Trustee1",
        TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4a"
    }
    data["seeds"]["Trustee1"] = trusteeSeed
    data["txns"].insert(0, t)
    return data


@pytest.fixture(scope="module")
def trusteeData(poolTxnTrusteeNames, updatedPoolTxnData):
    name = poolTxnTrusteeNames[0]
    seed = updatedPoolTxnData["seeds"][name]
    return name, seed.encode()


@pytest.fixture(scope="module")
def trusteeWallet(trusteeData):
    name, sigseed = trusteeData
    wallet = Wallet('trustee')
    signer = SimpleSigner(seed=sigseed)
    wallet.addIdentifier(signer=signer)
    return wallet


@pytest.fixture(scope="module")
def trustee(nodeSet, looper, tdir, up, trusteeWallet):
    return buildStewardClient(looper, tdir, trusteeWallet)


@pytest.fixture(scope="module")
def userWalletB(nodeSet, addedTrustAnchor, trustAnchorWallet, looper, trustAnchor):
    return addRole(looper, trustAnchor, trustAnchorWallet, 'userB', useDid=False)


@pytest.fixture("module")
def nodeThetaAdded(looper, nodeSet, tdirWithPoolTxns, tconf, steward,
                   stewardWallet, allPluginsPath, testNodeClass,
                   testClientClass, tdir):
    newStewardName = "testClientSteward" + randomString(3)
    newNodeName = "Theta"
    newSteward, newStewardWallet = getClientAddedWithRole(nodeSet, tdir,
                                                          looper, steward,
                                                          stewardWallet,
                                                          newStewardName, STEWARD)

    sigseed = randomString(32).encode()
    nodeSigner = SimpleSigner(seed=sigseed)

    (nodeIp, nodePort), (clientIp, clientPort) = genHa(2)

    data = {
        NODE_IP: nodeIp,
        NODE_PORT: nodePort,
        CLIENT_IP: clientIp,
        CLIENT_PORT: clientPort,
        ALIAS: newNodeName,
        SERVICES: [VALIDATOR, ]
    }

    node = Node(nodeSigner.identifier, data, newStewardWallet.defaultId)

    newStewardWallet.addNode(node)
    reqs = newStewardWallet.preparePending()
    req, = newSteward.submitReqs(*reqs)

    waitForSufficientRepliesForRequests(looper, newSteward, requests=[req])

    def chk():
        assert newStewardWallet.getNode(node.id).seqNo is not None

    timeout = plenumWaits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(chk, retryWait=1, timeout=timeout))

    initLocalKeys(newNodeName, tdirWithPoolTxns, sigseed, override=True)

    newNode = testNodeClass(newNodeName, basedirpath=tdir, config=tconf,
                            ha=(nodeIp, nodePort), cliha=(clientIp, clientPort),
                            pluginPaths=allPluginsPath)

    nodeSet.append(newNode)
    looper.add(newNode)
    looper.run(checkNodesConnected(nodeSet))
    ensureClientConnectedToNodesAndPoolLedgerSame(looper, steward,
                                                  *nodeSet)
    ensureClientConnectedToNodesAndPoolLedgerSame(looper, newSteward,
                                                  *nodeSet)
    return newSteward, newStewardWallet, newNode
