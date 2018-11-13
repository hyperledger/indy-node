import os
import logging

from plenum.common.member.member import Member
from plenum.common.txn_util import get_payload_data
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from plenum.common.signer_did import DidSigner
from stp_core.common.log import Logger

import warnings
from copy import deepcopy

from indy_common import strict_types

strict_types.defaultShouldCheck = True

import pytest

from plenum.common.constants import ALIAS, STEWARD, TRUSTEE

from indy_client.client.wallet.wallet import Wallet
from indy_common.constants import TRUST_ANCHOR
from indy_client.test.cli.helper import addTrusteeTxnsToGenesis, addTxnsToGenesisFile
from indy_node.test.helper import makePendingTxnsRequest, buildStewardClient, \
    TestNode
from indy_client.test.helper import genTestClient, TestClient, createNym

# noinspection PyUnresolvedReferences
from plenum.test.conftest import tdir, client_tdir, nodeReg, \
    whitelist, concerningLogLevels, logcapture, \
    tdirWithDomainTxns as PTdirWithDomainTxns, txnPoolNodeSet, poolTxnData, dirName, \
    poolTxnNodeNames, allPluginsPath, tdirWithNodeKeepInited, tdirWithPoolTxns, \
    poolTxnStewardData, poolTxnStewardNames, getValueFromModule, \
    txnPoolNodesLooper, patchPluginManager, tdirWithClientPoolTxns, \
    warncheck, warnfilters as plenum_warnfilters, setResourceLimits, do_post_node_creation

# noinspection PyUnresolvedReferences
from indy_common.test.conftest import tconf, general_conf_tdir, poolTxnTrusteeNames, \
    domainTxnOrderedFields, looper, config_helper_class, node_config_helper_class

from plenum.test.conftest import sdk_pool_handle as plenum_pool_handle, sdk_pool_data, sdk_wallet_steward, \
    sdk_wallet_handle, sdk_wallet_data, sdk_steward_seed, sdk_wallet_trustee, sdk_trustee_seed, trustee_data, \
    sdk_wallet_client, sdk_client_seed, poolTxnClientData, poolTxnClientNames, poolTxnData

Logger.setLogLevel(logging.DEBUG)


@pytest.fixture(scope="module")
def sdk_wallet_trust_anchor(looper, sdk_pool_handle, sdk_wallet_trustee):
    return sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee,
                           alias='TA-1', role='TRUST_ANCHOR')


@pytest.fixture(scope="session")
def warnfilters(plenum_warnfilters):
    def _():
        plenum_warnfilters()
        warnings.filterwarnings(
            'ignore', category=ResourceWarning, message='unclosed file')

    return _


@pytest.fixture(scope="module")
def updatedPoolTxnData(poolTxnData):
    data = deepcopy(poolTxnData)
    trusteeSeed = 'thisistrusteeseednotsteward12345'
    signer = DidSigner(seed=trusteeSeed.encode())
    t = Member.nym_txn(nym=signer.identifier,
                       name="Trustee1",
                       verkey=signer.verkey,
                       role=TRUSTEE,
                       txn_id="6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4a")
    data["seeds"]["Trustee1"] = trusteeSeed
    data["txns"].insert(0, t)
    return data


@pytest.fixture(scope="module")
def trusteeData(poolTxnTrusteeNames, updatedPoolTxnData):
    ret = []
    for name in poolTxnTrusteeNames:
        seed = updatedPoolTxnData["seeds"][name]
        txn = next(
            (txn for txn in updatedPoolTxnData["txns"] if get_payload_data(txn)[ALIAS] == name),
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
def trustee(nodeSet, looper, tdirWithClientPoolTxns, trusteeWallet):
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
    return [Member.nym_txn(
        nym=stewardWallet.defaultId,
        verkey=stewardWallet.getVerkey(),
        role=STEWARD,
        txn_id="9c86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b"
    )]


@pytest.fixture(scope="module")
def testNodeClass():
    return TestNode


@pytest.fixture(scope="module")
def testClientClass():
    return TestClient


@pytest.fixture(scope="module")
def tdirWithDomainTxns(PTdirWithDomainTxns, poolTxnTrusteeNames,
                       trusteeData, genesisTxns, domainTxnOrderedFields,
                       tconf):
    addTrusteeTxnsToGenesis(poolTxnTrusteeNames, trusteeData,
                            PTdirWithDomainTxns, tconf.domainTransactionsFile)
    addTxnsToGenesisFile(PTdirWithDomainTxns, tconf.domainTransactionsFile,
                         genesisTxns, domainTxnOrderedFields)
    return PTdirWithDomainTxns


@pytest.fixture(scope='module')
def sdk_pool_handle(plenum_pool_handle, nodeSet):
    return plenum_pool_handle


@pytest.fixture(scope="module")
def nodeSet(txnPoolNodeSet):
    return txnPoolNodeSet


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
def client_ledger_dir(client_tdir, tconf):
    return os.path.join(client_tdir, 'networks', tconf.NETWORK_NAME)


def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, str) and isinstance(right, str):
        if op in ('in', 'not in'):
            mod = 'not ' if 'not' in op else ''
            lines = ['    ' + s for s in right.split('\n')]
            return ['"{}" should {}be in...'.format(left, mod)] + lines
