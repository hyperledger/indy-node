import warnings

from plenum.common.eventually import eventually
from plenum.common.port_dispenser import genHa
from plenum.common.raet import initLocalKeep
from plenum.common.util import randomString
from plenum.test.helper import checkSufficientRepliesForRequests
from plenum.test.node_catchup.helper import \
    ensureClientConnectedToNodesAndPoolLedgerSame
from plenum.test.test_node import checkNodesConnected
from sovrin_client.client.wallet.node import Node

from sovrin_common import strict_types

# typecheck during tests
strict_types.defaultShouldCheck = True

import pytest

from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.ledger import Ledger
from ledger.serializers.compact_serializer import CompactSerializer

from plenum.common.signer_simple import SimpleSigner
from plenum.common.constants import VERKEY, NODE_IP, NODE_PORT, CLIENT_IP, CLIENT_PORT, \
    ALIAS, SERVICES, VALIDATOR, STEWARD, TXN_ID
from plenum.test.plugin.helper import getPluginPath

from sovrin_client.client.wallet.wallet import Wallet
from sovrin_common.constants import NYM, TRUST_ANCHOR
from sovrin_common.constants import TXN_TYPE, TARGET_NYM, ROLE
from sovrin_common.txn_util import getTxnOrderedFields
from sovrin_common.config_util import getConfig

from sovrin_node.test.helper import TestNode, \
    makePendingTxnsRequest, buildStewardClient

# noinspection PyUnresolvedReferences
from sovrin_client.test.helper import addRole, getClientAddedWithRole, \
    genTestClient, TestClient, createNym

# noinspection PyUnresolvedReferences
from sovrin_client.test.cli.helper import newCLI

# noinspection PyUnresolvedReferences
from sovrin_client.test.conftest import updatedPoolTxnData, trustAnchorWallet, \
    trustAnchor, tdirWithDomainTxnsUpdated, updatedDomainTxnFile, trusteeData,\
    trusteeWallet, poolTxnTrusteeNames, warnfilters as client_warnfilters

# noinspection PyUnresolvedReferences
from plenum.test.conftest import tdir, nodeReg, up, ready, \
    whitelist, concerningLogLevels, logcapture, keySharedNodes, \
    startedNodes, tdirWithDomainTxns, txnPoolNodeSet, poolTxnData, dirName, \
    poolTxnNodeNames, allPluginsPath, tdirWithNodeKeepInited, tdirWithPoolTxns, \
    poolTxnStewardData, poolTxnStewardNames, getValueFromModule, \
    txnPoolNodesLooper, nodeAndClientInfoFilePath, conf, patchPluginManager, \
    warncheck, warnfilters as plenum_warnfilters


@pytest.fixture(scope="session")
def warnfilters(client_warnfilters):
    def _():
        client_warnfilters()
        warnings.filterwarnings('ignore', category=DeprecationWarning, module='sovrin_common\.persistence\.identity_graph', lineno=734)
        warnings.filterwarnings('ignore', category=ResourceWarning, message='unclosed transport')
    return _


@pytest.fixture(scope="module")
def tconf(conf, tdir):
    conf.baseDir = tdir
    conf.MinSepBetweenNodeUpgrades = 5
    return conf


@pytest.fixture(scope="module")
def trustee(nodeSet, looper, tdir, up, trusteeWallet):
    return buildStewardClient(looper, tdir, trusteeWallet)


@pytest.fixture(scope="module")
def allPluginsPath():
    return [getPluginPath('stats_consumer')]


@pytest.fixture(scope="module")
def stewardWallet(poolTxnStewardData):
    name, sigseed = poolTxnStewardData
    wallet = Wallet('steward')
    signer = SimpleSigner(seed=sigseed)
    wallet.addIdentifier(signer=signer)
    return wallet


@pytest.fixture(scope="module")
def looper(txnPoolNodesLooper):
    return txnPoolNodesLooper


@pytest.fixture(scope="module")
def steward(nodeSet, looper, tdir, up, stewardWallet):
    return buildStewardClient(looper, tdir, stewardWallet)


@pytest.fixture(scope="module")
def genesisTxns(stewardWallet: Wallet, trusteeWallet: Wallet):
    nym = stewardWallet.defaultId
    return [
        {
            TXN_TYPE: NYM,
            TARGET_NYM: nym,
            TXN_ID: "9c86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b",
            ROLE: STEWARD,
            VERKEY: stewardWallet.getVerkey()
        },
    ]


@pytest.fixture(scope="module")
def domainTxnOrderedFields():
    return getTxnOrderedFields()


@pytest.fixture(scope="module")
def conf(tdir):
    return getConfig(tdir)


@pytest.fixture(scope="module")
def testNodeClass():
    return TestNode


@pytest.fixture(scope="module")
def testClientClass():
    return TestClient


@pytest.fixture(scope="module")
def nodeSet(tconf, updatedPoolTxnData, updatedDomainTxnFile, txnPoolNodeSet):
    return txnPoolNodeSet


@pytest.fixture(scope="module")
def addedTrustAnchor(nodeSet, steward, stewardWallet, looper,
                 trustAnchorWallet):
    createNym(looper,
              trustAnchorWallet.defaultId,
              steward,
              stewardWallet,
              role=TRUST_ANCHOR,
              verkey=trustAnchorWallet.getVerkey())
    return trustAnchorWallet


@pytest.fixture(scope="module")
def userWalletB(nodeSet, addedTrustAnchor, trustAnchorWallet, looper, trustAnchor):
    return addRole(looper, trustAnchor, trustAnchorWallet, 'userB', useDid=False)


@pytest.fixture(scope="module")
def userIdA(userWalletA):
    return userWalletA.defaultId


@pytest.fixture(scope="module")
def userIdB(userWalletB):
    return userWalletB.defaultId


@pytest.fixture(scope="module")
def userClientA(nodeSet, userWalletA, looper, tdir):
    u, _ = genTestClient(nodeSet, tmpdir=tdir, usePoolLedger=True)
    u.registerObserver(userWalletA.handleIncomingReply)
    looper.add(u)
    looper.run(u.ensureConnectedToNodes())
    makePendingTxnsRequest(u, userWalletA)
    return u


@pytest.fixture(scope="module")
def userClientB(nodeSet, userWalletB, looper, tdir):
    u, _ = genTestClient(nodeSet, tmpdir=tdir, usePoolLedger=True)
    u.registerObserver(userWalletB.handleIncomingReply)
    looper.add(u)
    looper.run(u.ensureConnectedToNodes())
    makePendingTxnsRequest(u, userWalletB)
    return u


def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, str) and isinstance(right, str):
        if op in ('in', 'not in'):
            mod = 'not ' if 'not' in op else ''
            lines = ['    ' + s for s in right.split('\n')]
            return ['"{}" should {}be in...'.format(left, mod)] + lines


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

    checkSufficientRepliesForRequests(looper, newSteward, [req, ])

    def chk():
        assert newStewardWallet.getNode(node.id).seqNo is not None

    looper.run(eventually(chk, retryWait=1, timeout=10))

    initLocalKeep(newNodeName, tdirWithPoolTxns, sigseed, override=True)

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
