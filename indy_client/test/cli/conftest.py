import json
import os
import re
import tempfile
from typing import List

import pytest
from indy_node.test.conftest import sdk_node_theta_added

from plenum.bls.bls_crypto_factory import create_default_bls_crypto_factory
from plenum.common.signer_did import DidSigner
from indy_common.config_helper import NodeConfigHelper
from ledger.genesis_txn.genesis_txn_file_util import create_genesis_txn_init_ledger
from plenum.common.txn_util import get_type

from stp_core.network.port_dispenser import genHa

from plenum.common.constants import ALIAS, NODE_IP, NODE_PORT, CLIENT_IP, \
    CLIENT_PORT, SERVICES, VALIDATOR, BLS_KEY, NODE, NYM, \
    BLS_KEY_PROOF
from plenum.common.constants import CLIENT_STACK_SUFFIX
from plenum.common.signer_simple import SimpleSigner
from plenum.common.util import randomString
from plenum.test import waits
from plenum.test.test_node import checkNodesConnected, ensureElectionsDone

from plenum.test.conftest import tdirWithNodeKeepInited
from stp_core.loop.eventually import eventually
from stp_core.common.log import getlogger
from indy_client.cli.helper import USAGE_TEXT, NEXT_COMMANDS_TO_TRY_TEXT
from indy_client.test.helper import createNym, buildStewardClient
from indy_common.constants import ENDPOINT, TRUST_ANCHOR
from indy_common.roles import Roles
from indy_common.test.conftest import domainTxnOrderedFields
from indy_node.test.helper import TestNode
from plenum.common.keygen_utils import initNodeKeysForBothStacks

# plenum.common.util.loggingConfigured = False

from stp_core.loop.looper import Looper
from plenum.test.cli.helper import newKeyPair, doByCtx

from indy_client.test.cli.helper import ensureNodesCreated, get_connection_request, \
    getPoolTxnData, newCLI, getCliBuilder, P, prompt_is, addNym
from indy_client.test.cli.helper import connect_and_check_output, disconnect_and_check_output
from indy_common.config_helper import ConfigHelper
from stp_core.crypto.util import randomSeed


@pytest.fixture("module")
def ledger_base_dir(tconf):
    return tconf.CLI_NETWORK_DIR


@pytest.yield_fixture(scope="session")
def cliTempLogger():
    file_name = "indy_cli_test.log"
    file_path = os.path.join(tempfile.tempdir, file_name)
    with open(file_path, 'w'):
        pass
    return file_path


@pytest.yield_fixture(scope="module")
def looper():
    with Looper(debug=False) as l:
        yield l


@pytest.fixture("module")
def cli(looper, client_tdir):
    return newCLI(looper, client_tdir)


@pytest.fixture(scope="module")
def CliBuilder(tdir, tdirWithPoolTxns, tdirWithDomainTxns,
               txnPoolNodesLooper, tconf, cliTempLogger):
    return getCliBuilder(
        tdir,
        tconf,
        tdirWithPoolTxns,
        tdirWithDomainTxns,
        logFileName=cliTempLogger,
        def_looper=txnPoolNodesLooper)


@pytest.fixture(scope="module")
def availableClaims():
    return ["Available Claim(s): {claims}"]


@pytest.fixture(scope="module")
def nymAddedOut():
    return ["Nym {remote} added"]


@pytest.yield_fixture(scope="module")
def poolCLI_baby(CliBuilder):
    yield from CliBuilder("pool")


@pytest.yield_fixture(scope="module")
def aliceCLI(CliBuilder):
    yield from CliBuilder("alice")


@pytest.fixture(scope="module")
def poolCLI(tdir, tconf, poolCLI_baby, poolTxnData, poolTxnNodeNames, txnPoolNodeSet):
    seeds = poolTxnData["seeds"]
    for nName in poolTxnNodeNames:
        seed = seeds[nName]
        use_bls = nName in poolTxnData['nodesWithBls']
        config_helper = NodeConfigHelper(nName, tconf, chroot=tdir)
        initNodeKeysForBothStacks(nName, config_helper.keys_dir,
                                  seed, override=True, use_bls=use_bls)
    for node in txnPoolNodeSet:
        poolCLI_baby.nodes[node.name] = node
    return poolCLI_baby


@pytest.fixture(scope="module")
def poolNodesCreated(poolCLI, poolTxnNodeNames):
    # ensureNodesCreated(poolCLI, poolTxnNodeNames)
    return poolCLI


@pytest.fixture("module")
def ctx():
    """
    Provides a simple container for test context. Assists with 'be' and 'do'.
    """
    return {}


@pytest.fixture("module")
def be(ctx):
    """
    Fixture that is a 'be' function that closes over the test context.
    'be' allows to change the current cli in the context.
    """

    def _(cli):
        ctx['current_cli'] = cli

    return _


@pytest.fixture("module")
def do(ctx):
    """
    Fixture that is a 'do' function that closes over the test context
    'do' allows to call the do method of the current cli from the context.
    """
    return doByCtx(ctx)


@pytest.fixture(scope="module")
def dump(ctx):
    def _dump():
        logger = getlogger()

        cli = ctx['current_cli']
        nocli = {"cli": False}
        wrts = ''.join(cli.cli.output.writes)
        logger.info('=========================================', extra=nocli)
        logger.info('|             OUTPUT DUMP               |', extra=nocli)
        logger.info('-----------------------------------------', extra=nocli)
        for w in wrts.splitlines():
            logger.info('> ' + w, extra=nocli)
        logger.info('=========================================', extra=nocli)

    return _dump


@pytest.fixture(scope="module")
def bookmark(ctx):
    BM = '~bookmarks~'
    if BM not in ctx:
        ctx[BM] = {}
    return ctx[BM]


@pytest.fixture(scope="module")
def current_cli(ctx):
    def _():
        return ctx['current_cli']

    return _


@pytest.fixture(scope="module")
def get_bookmark(bookmark, current_cli):
    def _():
        return bookmark.get(current_cli(), 0)

    return _


@pytest.fixture(scope="module")
def set_bookmark(bookmark, current_cli):
    def _(val):
        bookmark[current_cli()] = val

    return _


@pytest.fixture(scope="module")
def inc_bookmark(get_bookmark, set_bookmark):
    def _(inc):
        val = get_bookmark()
        set_bookmark(val + inc)

    return _


@pytest.fixture(scope="module")
def expect(current_cli, get_bookmark, inc_bookmark):
    def _expect(expected, mapper=None, line_no=None,
                within=None, ignore_extra_lines=None):
        cur_cli = current_cli()

        def _():
            expected_ = expected if not mapper \
                else [s.format(**mapper) for s in expected]
            assert isinstance(expected_, List)
            bm = get_bookmark()
            actual = ''.join(cur_cli.cli.output.writes).splitlines()[bm:]
            assert isinstance(actual, List)
            explanation = ''
            expected_index = 0
            for i in range(min(len(expected_), len(actual))):
                e = expected_[expected_index]
                assert isinstance(e, str)
                a = actual[i]
                assert isinstance(a, str)
                is_p = isinstance(e, P)
                if (not is_p and a != e) or (is_p and not e.match(a)):
                    if ignore_extra_lines:
                        continue
                    explanation += "line {} doesn't match\n" \
                                   "  expected: {}\n" \
                                   "    actual: {}\n".format(i, e, a)
                expected_index += 1

            if len(expected_) > len(actual):
                for e in expected_:
                    try:
                        p = re.compile(e) if isinstance(e, P) else None
                    except Exception as err:
                        explanation += "ERROR COMPILING REGEX for {}: {}\n". \
                            format(e, err)
                    for a in actual:
                        if (p and p.fullmatch(a)) or a == e:
                            break
                    else:
                        explanation += "missing: {}\n".format(e)

            if len(expected_) < len(actual) and ignore_extra_lines is None:
                for a in actual:
                    for e in expected_:
                        p = re.compile(e) if isinstance(e, P) else None
                        if (p and p.fullmatch(a)) or a == e:
                            break
                    else:
                        explanation += "extra: {}\n".format(a)

            if explanation:
                explanation += "\nexpected:\n"
                for x in expected_:
                    explanation += "  > {}\n".format(x)
                explanation += "\nactual:\n"
                for x in actual:
                    explanation += "  > {}\n".format(x)
                if line_no:
                    explanation += "section ends line number: {}\n".format(
                        line_no)
                pytest.fail(''.join(explanation))
            else:
                inc_bookmark(len(actual))

        if within:
            cur_cli.looper.run(eventually(_, timeout=within))
        else:
            _()

    return _expect


@pytest.fixture(scope="module")
def steward(poolNodesCreated, looper, tdir, stewardWallet):
    return buildStewardClient(looper, tdir, stewardWallet)


@pytest.yield_fixture(scope="module")  # noqa
def trusteeCLI(CliBuilder, poolTxnTrusteeNames):
    yield from CliBuilder(poolTxnTrusteeNames[0])


@pytest.fixture(scope="module")
def trusteeMap(trusteeWallet):
    return {
        'trusteeSeed': bytes(trusteeWallet._signerById(
            trusteeWallet.defaultId).sk).decode(),
        'trusteeIdr': trusteeWallet.defaultId,
    }


@pytest.fixture(scope="module")
def trusteeCli(be, do, trusteeMap, poolNodesStarted, nymAddedOut, trusteeCLI):
    be(trusteeCLI)
    do('new key with seed {trusteeSeed}', expect=[
        'DID for key is {trusteeIdr}',
        'Current DID set to {trusteeIdr}'],
       mapper=trusteeMap)

    if not trusteeCLI._isConnectedToAnyEnv():
        connect_and_check_output(do, trusteeCLI.txn_dir)

    return trusteeCLI


@pytest.fixture(scope="module")
def poolNodesStarted(be, do, poolCLI):
    be(poolCLI)
    return poolCLI


@pytest.fixture(scope='module')
def newStewardVals():
    newStewardSeed = randomSeed()
    signer = DidSigner(seed=newStewardSeed)
    return {
        'newStewardSeed': newStewardSeed.decode(),
        'newStewardIdr': signer.identifier,
        'newStewardVerkey': signer.verkey
    }


@pytest.fixture(scope='function')
def new_bls_keys():
    _, bls_key, key_proof = create_default_bls_crypto_factory().generate_bls_keys()
    return bls_key, key_proof


@pytest.fixture(scope='module')
def newNodeVals():
    newNodeSeed = randomSeed()
    nodeIp, nodePort = genHa()
    clientIp, clientPort = genHa()
    _, bls_key, key_proof = create_default_bls_crypto_factory().generate_bls_keys()

    newNodeData = {
        NODE_IP: nodeIp,
        NODE_PORT: nodePort,
        CLIENT_IP: clientIp,
        CLIENT_PORT: clientPort,
        ALIAS: randomString(6),
        SERVICES: [VALIDATOR],
        BLS_KEY: bls_key,
        BLS_KEY_PROOF: key_proof
    }

    return {
        'newNodeSeed': newNodeSeed.decode(),
        'newNodeIdr': SimpleSigner(seed=newNodeSeed).identifier,
        'newNodeData': newNodeData
    }


@pytest.fixture(scope='module')
def nodeValsEmptyData(newNodeVals):
    node_vals = {}
    node_vals['newNodeData'] = {}
    node_vals['newNodeIdr'] = newNodeVals['newNodeIdr']
    return node_vals


@pytest.yield_fixture(scope="module")
def cliWithNewStewardName(CliBuilder):
    yield from CliBuilder("newSteward")


@pytest.fixture(scope='module')
def newStewardCli(be, do, poolNodesStarted, trusteeCli,
                  cliWithNewStewardName, newStewardVals):
    be(trusteeCli)
    if not trusteeCli._isConnectedToAnyEnv():
        connect_and_check_output(do, trusteeCli.txn_dir)

    do('send NYM dest={{newStewardIdr}} role={role} verkey={{newStewardVerkey}}'
       .format(role=Roles.STEWARD.name),
       within=3,
       expect='Nym {newStewardIdr} added',
       mapper=newStewardVals)

    be(cliWithNewStewardName)

    do('new key with seed {newStewardSeed}', expect=[
        'DID for key is {newStewardIdr}',
        'Current DID set to {newStewardIdr}'],
       mapper=newStewardVals)

    if not cliWithNewStewardName._isConnectedToAnyEnv():
        connect_and_check_output(do, cliWithNewStewardName.txn_dir)

    return cliWithNewStewardName


@pytest.fixture(scope="module")
def newNodeAdded(looper, nodeSet, tdir, tconf, sdk_pool_handle,
                 sdk_wallet_trustee, allPluginsPath):
    new_steward_wallet, new_node = sdk_node_theta_added(looper,
                                                        nodeSet,
                                                        tdir,
                                                        tconf,
                                                        sdk_pool_handle,
                                                        sdk_wallet_trustee,
                                                        allPluginsPath,
                                                        node_config_helper_class=NodeConfigHelper,
                                                        testNodeClass=TestNode,
                                                        name='')
    return new_steward_wallet, new_node


@pytest.fixture(scope='module')
def nodeIds(poolNodesStarted):
    return next(iter(poolNodesStarted.nodes.values())).poolManager.nodeIds
