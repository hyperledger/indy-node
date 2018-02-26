import os
import logging

import base58

from anoncreds.protocol.utils import randomString
from plenum.common.keygen_utils import initLocalKeys
from plenum.common.signer_did import DidSigner
from plenum.common.util import friendlyToRaw
from plenum.test import waits as plenumWaits
from stp_core.common.log import Logger

from stp_core.loop.eventually import eventually
from indy_client.test.constants import primes
import warnings
from copy import deepcopy

from indy_common import strict_types

# typecheck during tests
from stp_core.network.port_dispenser import genHa

strict_types.defaultShouldCheck = True

import pytest

from plenum.common.constants import VERKEY, ALIAS, STEWARD, TXN_ID, TRUSTEE, TYPE

from indy_client.client.wallet.wallet import Wallet
from indy_common.constants import NYM, TRUST_ANCHOR
from indy_common.constants import TXN_TYPE, TARGET_NYM, ROLE
from indy_client.test.cli.helper import newCLI, addTrusteeTxnsToGenesis, addTxnToGenesisFile
from indy_node.test.helper import makePendingTxnsRequest, buildStewardClient, \
    TestNode
from indy_client.test.helper import addRole, genTestClient, TestClient, createNym

# noinspection PyUnresolvedReferences
from plenum.test.conftest import tdir, client_tdir, nodeReg, up, ready, \
    whitelist, concerningLogLevels, logcapture, keySharedNodes, \
    startedNodes, tdirWithDomainTxns, txnPoolNodeSet, poolTxnData, dirName, \
    poolTxnNodeNames, allPluginsPath, tdirWithNodeKeepInited, tdirWithPoolTxns, \
    poolTxnStewardData, poolTxnStewardNames, getValueFromModule, \
    txnPoolNodesLooper, patchPluginManager, tdirWithClientPoolTxns, \
    warncheck, warnfilters as plenum_warnfilters, setResourceLimits, do_post_node_creation

# noinspection PyUnresolvedReferences
from indy_common.test.conftest import tconf, general_conf_tdir, poolTxnTrusteeNames, \
    domainTxnOrderedFields, looper, config_helper_class, node_config_helper_class

from plenum.test.conftest import sdk_pool_handle, sdk_pool_name, sdk_wallet_steward, sdk_wallet_handle, \
    sdk_wallet_name, sdk_steward_seed

Logger.setLogLevel(logging.DEBUG)


@pytest.fixture(scope="session")
def warnfilters(plenum_warnfilters):
    def _():
        plenum_warnfilters()
        warnings.filterwarnings(
            'ignore', category=ResourceWarning, message='unclosed file')
    return _


@pytest.fixture(scope="module")
def primes1():
    P_PRIME1, Q_PRIME1 = primes.get("prime1")
    return dict(p_prime=P_PRIME1, q_prime=Q_PRIME1)


@pytest.fixture(scope="module")
def primes2():
    P_PRIME2, Q_PRIME2 = primes.get("prime2")
    return dict(p_prime=P_PRIME2, q_prime=Q_PRIME2)


@pytest.fixture(scope="module")
def updatedPoolTxnData(poolTxnData):
    data = deepcopy(poolTxnData)
    trusteeSeed = 'thisistrusteeseednotsteward12345'
    signer = DidSigner(seed=trusteeSeed.encode())
    t = {
        TARGET_NYM: signer.identifier,
        VERKEY: signer.verkey,
        ROLE: TRUSTEE,
        TYPE: NYM,
        ALIAS: "Trustee1",
        TXN_ID: "6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4a"}
    data["seeds"]["Trustee1"] = trusteeSeed
    data["txns"].insert(0, t)
    return data


@pytest.fixture(scope="module")
def trusteeData(poolTxnTrusteeNames, updatedPoolTxnData):
    ret = []
    for name in poolTxnTrusteeNames:
        seed = updatedPoolTxnData["seeds"][name]
        txn = next(
            (txn for txn in updatedPoolTxnData["txns"] if txn[ALIAS] == name),
            None)
        ret.append((name, seed.encode(), txn))
    return ret


@pytest.fixture(scope="module")
def trusteeWallet(trusteeData):
    name, sigseed, txn = trusteeData[0]
    wallet = Wallet('trustee')
    signer = DidSigner(seed=sigseed)
    wallet.addIdentifier(signer=signer)
    return wallet


# TODO: This fixture is present in indy_node too, it should be
# indy_common's conftest.
@pytest.fixture(scope="module")
# TODO devin
def trustee(nodeSet, looper, tdirWithClientPoolTxns, up, trusteeWallet):
    return buildStewardClient(looper, tdirWithClientPoolTxns, trusteeWallet)


@pytest.fixture(scope="module")
def stewardWallet(poolTxnStewardData):
    name, sigseed = poolTxnStewardData
    wallet = Wallet('steward')
    signer = DidSigner(seed=sigseed)
    wallet.addIdentifier(signer=signer)
    return wallet


@pytest.fixture(scope="module")
def steward(nodeSet, looper, tdirWithClientPoolTxns, stewardWallet):
    return buildStewardClient(looper, tdirWithClientPoolTxns, stewardWallet)


@pytest.fixture(scope="module")
def genesisTxns(stewardWallet: Wallet, trusteeWallet: Wallet):
    nym = stewardWallet.defaultId
    return [{TXN_TYPE: NYM,
             TARGET_NYM: nym,
             TXN_ID: "9c86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b",
             ROLE: STEWARD,
             VERKEY: stewardWallet.getVerkey()},
            ]


@pytest.fixture(scope="module")
def testNodeClass():
    return TestNode


@pytest.fixture(scope="module")
def testClientClass():
    return TestClient


@pytest.fixture(scope="module")
def tdirWithDomainTxnsUpdated(tdirWithDomainTxns, poolTxnTrusteeNames,
                              trusteeData, tconf):
    addTrusteeTxnsToGenesis(poolTxnTrusteeNames, trusteeData,
                            tdirWithDomainTxns, tconf.domainTransactionsFile)
    return tdirWithDomainTxns


@pytest.fixture(scope="module")
def updatedDomainTxnFile(tdirWithDomainTxnsUpdated, genesisTxns,
                         domainTxnOrderedFields, tconf):
    addTxnToGenesisFile(tdirWithDomainTxnsUpdated, tconf.domainTransactionsFile,
                        genesisTxns, domainTxnOrderedFields)


@pytest.fixture(scope="module")
def nodeSet(tconf, updatedPoolTxnData, updatedDomainTxnFile, txnPoolNodeSet):
    return txnPoolNodeSet


@pytest.fixture(scope="module")
def client1Signer():
    seed = b'client1Signer secret key........'
    signer = DidSigner(seed=seed)
    testable_verkey = friendlyToRaw(signer.identifier)
    testable_verkey += friendlyToRaw(signer.verkey[1:])
    testable_verkey = base58.b58encode(testable_verkey)
    assert testable_verkey == '6JvpZp2haQgisbXEXE9NE6n3Tuv77MZb5HdF9jS5qY8m'
    return signer


@pytest.fixture("module")
def trustAnchorCli(looper, tdir):
    return newCLI(looper, tdir)


@pytest.fixture(scope="module")
def clientAndWallet1(client1Signer, looper, nodeSet, tdirWithClientPoolTxns, up):
    client, wallet = genTestClient(nodeSet, tmpdir=tdirWithClientPoolTxns, usePoolLedger=True)
    wallet = Wallet(client.name)
    wallet.addIdentifier(signer=client1Signer)
    return client, wallet


@pytest.fixture(scope="module")
def client1(clientAndWallet1, looper):
    client, wallet = clientAndWallet1
    looper.add(client)
    looper.run(client.ensureConnectedToNodes())
    return client


@pytest.fixture(scope="module")
def wallet1(clientAndWallet1):
    return clientAndWallet1[1]


@pytest.fixture(scope="module")
def trustAnchorWallet():
    wallet = Wallet('trustAnchor')
    seed = b'trust anchors are people too....'
    wallet.addIdentifier(seed=seed)
    return wallet


@pytest.fixture(scope="module")
def trustAnchor(nodeSet, addedTrustAnchor, trustAnchorWallet, looper, tdirWithClientPoolTxns):
    s, _ = genTestClient(nodeSet, tmpdir=tdirWithClientPoolTxns, usePoolLedger=True)
    s.registerObserver(trustAnchorWallet.handleIncomingReply)
    looper.add(s)
    looper.run(s.ensureConnectedToNodes())
    makePendingTxnsRequest(s, trustAnchorWallet)
    return s


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
def userWalletA(nodeSet, addedTrustAnchor,
                trustAnchorWallet, looper, trustAnchor):
    return addRole(looper, trustAnchor, trustAnchorWallet, 'userA',
                   addVerkey=False)


@pytest.fixture(scope="module")
def userWalletB(nodeSet, addedTrustAnchor,
                trustAnchorWallet, looper, trustAnchor):
    return addRole(looper, trustAnchor, trustAnchorWallet, 'userB',
                   addVerkey=False)


@pytest.fixture(scope="module")
def userIdA(userWalletA):
    return userWalletA.defaultId


@pytest.fixture(scope="module")
def userIdB(userWalletB):
    return userWalletB.defaultId


@pytest.fixture(scope="module")
def userClientA(nodeSet, userWalletA, looper, tdirWithClientPoolTxns):
    u, _ = genTestClient(nodeSet, tmpdir=tdirWithClientPoolTxns, usePoolLedger=True)
    u.registerObserver(userWalletA.handleIncomingReply)
    looper.add(u)
    looper.run(u.ensureConnectedToNodes())
    makePendingTxnsRequest(u, userWalletA)
    return u


@pytest.fixture(scope="module")
def userClientB(nodeSet, userWalletB, looper, tdirWithClientPoolTxns):
    u, _ = genTestClient(nodeSet, tmpdir=tdirWithClientPoolTxns, usePoolLedger=True)
    u.registerObserver(userWalletB.handleIncomingReply)
    looper.add(u)
    looper.run(u.ensureConnectedToNodes())
    makePendingTxnsRequest(u, userWalletB)
    return u


@pytest.fixture(scope="module")
def client_ledger_dir(client_tdir, tconf):
    return os.path.join(client_tdir, 'networks', tconf.NETWORK_NAME)


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
    newSteward, newStewardWallet = getClientAddedWithRole(
        nodeSet, tdir, looper, steward, stewardWallet, newStewardName, STEWARD)

    sigseed = randomString(32).encode()
    nodeSigner = DidSigner(seed=sigseed)

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
    req = newSteward.submitReqs(*reqs)[0][0]

    waitForSufficientRepliesForRequests(looper, newSteward, requests=[req])

    def chk():
        assert newStewardWallet.getNode(node.id).seqNo is not None

    timeout = waits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(chk, retryWait=1, timeout=timeout))

    initLocalKeys(newNodeName, tdirWithPoolTxns, sigseed, override=True)

    newNode = testNodeClass(newNodeName, basedirpath=tdir, base_data_dir=tdir, config=tconf,
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
