import json
import os
import re
from _sha256 import sha256
from typing import Dict

from libnacl import randombytes

from plenum.common import util
from plenum.common.signer_did import DidSigner
from plenum.common.util import rawToFriendly

from plenum.test import waits
from stp_core.loop.eventually import eventually
from stp_core.loop.looper import Looper

from stp_core.common.log import getlogger

from plenum.common.signer_simple import SimpleSigner
from plenum.common.constants import TARGET_NYM, ROLE, NODE, TXN_TYPE, DATA, \
    CLIENT_PORT, NODE_PORT, NODE_IP, ALIAS, CLIENT_IP, TXN_ID, SERVICES, \
    VALIDATOR, STEWARD
from plenum.common.types import f
from plenum.test.cli.helper import TestCliCore, assertAllNodesCreated, \
    waitAllNodesStarted, newCLI as newPlenumCLI
from plenum.test.helper import initDirWithGenesisTxns
from plenum.test.testable import spyable
from sovrin_client.cli.cli import SovrinCli
from sovrin_client.client.wallet.link import Link
from sovrin_common.constants import Environment
from stp_core.network.port_dispenser import genHa
from sovrin_common.constants import NYM
from sovrin_client.test.client.TestClient import TestClient
from sovrin_common.txn_util import getTxnOrderedFields
from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.ledger import Ledger
from ledger.serializers.compact_serializer import CompactSerializer
from sovrin_common.roles import Roles

logger = getlogger()


@spyable(methods=[SovrinCli.print, SovrinCli.printTokens])
class TestCLI(SovrinCli, TestCliCore):
    pass
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     # new = logging.StreamHandler(sys.stdout)
    #     # Logger()._setHandler('std', new)
    #     Logger().enableStdLogging()


def sendNym(cli, nym, role):
    cli.enterCmd("send NYM {}={} "
                 "{}={}".format(TARGET_NYM, nym,
                                ROLE, role))


def checkGetNym(cli, nym):
    printeds = ["Getting nym {}".format(nym), "Sequence number for NYM {} is "
        .format(nym)]
    checks = [x in cli.lastCmdOutput for x in printeds]
    assert all(checks)
    # TODO: These give NameError, don't know why
    # assert all([x in cli.lastCmdOutput for x in printeds])
    # assert all(x in cli.lastCmdOutput for x in printeds)


def checkAddAttr(cli):
    assert "Adding attributes" in cli.lastCmdOutput


def chkNymAddedOutput(cli, nym):
    checks = [x['msg'] == "Nym {} added".format(nym) for x in cli.printeds]
    assert any(checks)


def checkConnectedToEnv(cli):
    # TODO: Improve this
    assert "now connected to" in cli.lastCmdOutput



def ensureConnectedToTestEnv(be, do, cli):
    be(cli)
    if not cli._isConnectedToAnyEnv():
        timeout = waits.expectedClientToPoolConnectionTimeout(len(cli.nodeReg))
        do('connect test', within=timeout,
           expect=['Connected to test'])


def ensureNymAdded(be, do, cli, nym, role=None):
    ensureConnectedToTestEnv(be, do, cli)
    cmd = "send NYM {dest}={nym}".format(dest=TARGET_NYM, nym=nym)
    if role:
        cmd += " {ROLE}={role}".format(ROLE=ROLE, role=role)
    cli.enterCmd(cmd)
    timeout = waits.expectedTransactionExecutionTime(len(cli.nodeReg))
    cli.looper.run(
        eventually(chkNymAddedOutput, cli, nym, retryWait=1, timeout=timeout))

    timeout = waits.expectedTransactionExecutionTime(len(cli.nodeReg))
    cli.enterCmd("send GET_NYM {dest}={nym}".format(dest=TARGET_NYM, nym=nym))
    cli.looper.run(eventually(checkGetNym, cli, nym, retryWait=1, timeout=timeout))

    cli.enterCmd('send ATTRIB {dest}={nym} raw={raw}'.
                 format(dest=TARGET_NYM, nym=nym,
                        # raw='{\"attrName\":\"attrValue\"}'))
                        raw=json.dumps({"attrName": "attrValue"})))
    timeout = waits.expectedTransactionExecutionTime(len(cli.nodeReg))
    cli.looper.run(eventually(checkAddAttr, cli, retryWait=1, timeout=timeout))


def ensureNodesCreated(cli, nodeNames):
    cli.enterCmd("new node all")
    # TODO: Why 2 different interfaces one with list and one with varags
    assertAllNodesCreated(cli, nodeNames)
    waitAllNodesStarted(cli, *nodeNames)


def getFileLines(path, caller_file=None):
    filePath = SovrinCli._getFilePath(path, caller_file)
    with open(filePath, 'r') as fin:
        lines = fin.read().splitlines()
    return lines


def doubleBraces(lines):
    # TODO this is needed to accommodate mappers in 'do' fixture; this can be
    # removed when refactoring to the new 'expect' fixture is complete
    alteredLines = []
    for line in lines:
        alteredLines.append(line.replace('{', '{{').replace('}', '}}'))
    return alteredLines


def getLinkInvitation(name, wallet) -> Link:
    existingLinkInvites = wallet.getMatchingLinks(name)
    li = existingLinkInvites[0]
    return li


def getPoolTxnData(poolId, newPoolTxnNodeNames):
    data={}
    data["seeds"]={}
    data["txns"]=[]
    for index, n in enumerate(newPoolTxnNodeNames, start=1):
        newStewardAlias = poolId + "Steward" + str(index)
        stewardSeed = (newStewardAlias + "0" * (32 - len(newStewardAlias))).encode()
        data["seeds"][newStewardAlias] = stewardSeed
        stewardSigner = SimpleSigner(seed=stewardSeed)
        data["txns"].append({
                TARGET_NYM: stewardSigner.verkey,
                ROLE: STEWARD, TXN_TYPE: NYM,
                ALIAS: poolId + "Steward" + str(index),
                TXN_ID: sha256("{}".format(stewardSigner.verkey).encode()).hexdigest()
        })

        newNodeAlias = n
        nodeSeed = (newNodeAlias + "0" * (32 - len(newNodeAlias))).encode()
        data["seeds"][newNodeAlias] = nodeSeed
        nodeSigner = SimpleSigner(seed=nodeSeed)
        data["txns"].append({
                TARGET_NYM: nodeSigner.verkey,
                TXN_TYPE: NODE,
                f.IDENTIFIER.nm: stewardSigner.verkey,
                DATA: {
                    CLIENT_IP: "127.0.0.1",
                    ALIAS: newNodeAlias,
                    NODE_IP: "127.0.0.1",
                    NODE_PORT: genHa()[1],
                    CLIENT_PORT: genHa()[1],
                    SERVICES: [VALIDATOR],
                },
                TXN_ID: sha256("{}".format(nodeSigner.verkey).encode()).hexdigest()
        })
    return data


def prompt_is(prompt):
    def x(cli):
        assert cli.currPromptText == prompt, \
            "expected prompt: {}, actual prompt: {}".\
                format(prompt, cli.currPromptText)
    return x


def addTxnToFile(dir, file, txns, fields=getTxnOrderedFields()):
    ledger = Ledger(CompactMerkleTree(),
                    dataDir=dir,
                    serializer=CompactSerializer(fields=fields),
                    fileName=file)
    for txn in txns:
        ledger.add(txn)
    ledger.stop()


def addTrusteeTxnsToGenesis(trusteeList, trusteeData, txnDir, txnFileName):
    added = 0
    if trusteeList and len(trusteeList) and trusteeData:
        txns=[]
        for trusteeToAdd in trusteeList:
            try:
                trusteeData = next((data for data in trusteeData if data[0] == trusteeToAdd))
                name, seed, txn = trusteeData
                txns.append(txn)
            except StopIteration as e:
                logger.debug('{} not found in trusteeData'.format(trusteeToAdd))
        addTxnToFile(txnDir, txnFileName, txns)
    return added


def newCLI(looper, tdir, subDirectory=None, conf=None, poolDir=None,
           domainDir=None, multiPoolNodes=None, unique_name=None,
           logFileName=None, cliClass=TestCLI, name=None, agent=None):
    tempDir = os.path.join(tdir, subDirectory) if subDirectory else tdir
    if poolDir or domainDir:
        initDirWithGenesisTxns(tempDir, conf, poolDir, domainDir)

    if multiPoolNodes:
        conf.ENVS = {}
        for pool in multiPoolNodes:
            conf.poolTransactionsFile = "pool_transactions_{}".format(pool.name)
            conf.domainTransactionsFile = "transactions_{}".format(pool.name)
            conf.ENVS[pool.name] = \
                Environment("pool_transactions_{}".format(pool.name),
                                "transactions_{}".format(pool.name))
            initDirWithGenesisTxns(
                tempDir, conf, os.path.join(pool.tdirWithPoolTxns, pool.name),
                os.path.join(pool.tdirWithDomainTxns, pool.name))
    from sovrin_node.test.helper import TestNode
    new_cli = newPlenumCLI(looper, tempDir, cliClass=cliClass,
                           nodeClass=TestNode, clientClass=TestClient, config=conf,
                           unique_name=unique_name, logFileName=logFileName,
                           name=name, agentCreator=True)
    if isinstance(new_cli, SovrinCli) and agent is not None:
        new_cli.agent = agent
    return new_cli


def getCliBuilder(tdir, tconf, tdirWithPoolTxns, tdirWithDomainTxns,
                  logFileName=None, multiPoolNodes=None, cliClass=TestCLI,
                  name=None, agent=None):
    def _(space,
          looper=None,
          unique_name=None):
        def new():
            c = newCLI(looper,
                       tdir,
                       subDirectory=space,
                       conf=tconf,
                       poolDir=tdirWithPoolTxns,
                       domainDir=tdirWithDomainTxns,
                       multiPoolNodes=multiPoolNodes,
                       unique_name=unique_name or space,
                       logFileName=logFileName,
                       cliClass=cliClass,
                       name=name,
                       agent=agent)
            return c
        if looper:
            yield new()
        else:
            with Looper(debug=False) as looper:
                yield new()
    return _


# marker class for regex pattern
class P(str):
    def match(self, other):
        return re.match('^{}$'.format(self), other)


def check_wallet(cli,
                 totalLinks=None,
                 totalAvailableClaims=None,
                 totalSchemas=None,
                 totalClaimsRcvd=None,
                 within=None):
    async def check():
        actualLinks = len(cli.activeWallet._links)
        assert (totalLinks is None or (totalLinks == actualLinks)),\
            'links expected to be {} but is {}'.format(totalLinks, actualLinks)

        tac = 0
        for li in cli.activeWallet._links.values():
            tac += len(li.availableClaims)

        assert (totalAvailableClaims is None or
                totalAvailableClaims == tac), \
            'available claims {} must be equal to {}'.\
                format(tac, totalAvailableClaims)

        if cli.agent.prover is None:
            assert (totalSchemas + totalClaimsRcvd) == 0
        else:
            w = cli.agent.prover.wallet
            actualSchemas = len(await w.getAllSchemas())
            assert (totalSchemas is None or
                    totalSchemas == actualSchemas),\
                'schemas expected to be {} but is {}'.\
                    format(totalSchemas, actualSchemas)

            assert (totalClaimsRcvd is None or
                    totalClaimsRcvd == len((await w.getAllClaimsSignatures()).keys()))

    if within:
        cli.looper.run(eventually(check, timeout=within))
    else:
        cli.looper.run(check)


def wallet_state(totalLinks=0,
                 totalAvailableClaims=0,
                 totalSchemas=0,
                 totalClaimsRcvd=0):
    return locals()


def addAgent(be, do, userCli, mapper):
    addNym(be,
           do,
           userCli,
           mapper['remote'],
           verkey=mapper.get('remote-verkey', None),
           role=Roles.TRUST_ANCHOR.name)
    return userCli


def addNym(be, do, userCli, idr, verkey=None, role=None):
    be(userCli)

    ensureConnectedToTestEnv(be, do, userCli)

    cmd = 'send NYM dest={}'.format(idr)
    if role is not None:
        cmd += ' role={}'.format(role)
    if verkey is not None:
        cmd += ' verkey={}'.format(verkey)

    do(cmd, expect='Nym {} added'.format(idr), within=2)


def newKey(be, do, userCli, seed=None):
    be(userCli)
    cmd = 'new key'
    if seed is not None:
        cmd += ' with seed {}'.format(seed)

    do(cmd, expect='Current identifier set to')


def getAgentCliHelpString():
    return """Sovrin-CLI, a simple command-line interface for a Sovrin Identity platform.
   Commands:
       help - Shows this or specific help message for given command
         Usage:
            help [<command name>]
       prompt - Changes the prompt to given principal (a person like Alice, an organization like Faber College, or an IoT-style thing)
       list keyrings - Lists all keyrings
       list ids - Lists all identifiers of active keyring
       show - Shows content of given file
       show link - Shows link info in case of one matching link, otherwise shows all the matching link names
       ping - Pings given remote's endpoint
       list links - List available links in active wallet
       send proofreq - Send a proof request
       license - Shows the license
       exit - Exit the command-line interface ('quit' also works)"""


def getTotalLinks(userCli):
    return len(userCli.activeWallet._links)


def getTotalAvailableClaims(userCli):
    availableClaimsCount = 0
    for li in userCli.activeWallet._links.values():
        availableClaimsCount += len(li.availableClaims)
    return availableClaimsCount


def getTotalSchemas(userCli):
    async def getTotalSchemasCoro():
        return 0 if userCli.agent.prover is None \
            else len(await userCli.agent.prover.wallet.getAllSchemas())
    return userCli.looper.run(getTotalSchemasCoro)


def getTotalClaimsRcvd(userCli):
    async def getTotalClaimsRcvdCoro():
        return 0 if userCli.agent.prover is None \
            else len((await userCli.agent.prover.wallet.getAllClaimsSignatures()).keys())
    return userCli.looper.run(getTotalClaimsRcvdCoro)


def getWalletState(userCli):
    totalLinks = getTotalLinks(userCli)
    totalAvailClaims = getTotalAvailableClaims(userCli)
    totalSchemas = getTotalSchemas(userCli)
    totalClaimsRcvd = getTotalClaimsRcvd(userCli)
    return wallet_state(totalLinks, totalAvailClaims, totalSchemas,
                        totalClaimsRcvd)


def doSendNodeCmd(do, nodeVals, expMsgs=None):
    expect = expMsgs or ['Node request completed']
    do('send NODE dest={newNodeIdr} data={newNodeData}',
       within=8, expect=expect, mapper=nodeVals)


def createUuidIdentifier():
    return rawToFriendly(randombytes(16))


def createUuidIdentifierAndFullVerkey(seed=None):
    didSigner = DidSigner(identifier=createUuidIdentifier(), seed=seed)
    return didSigner.identifier, didSigner.verkey


def createHalfKeyIdentifierAndAbbrevVerkey(seed=None):
    didSigner = DidSigner(seed=seed)
    return didSigner.identifier, didSigner.verkey


def createCryptonym(seed=None):
    return SimpleSigner(seed=seed).identifier


def compareAgentIssuerWallet(unpersistedWallet, restoredWallet):
    def compare(old, new):
        if isinstance(old, Dict):
            for k, v in old.items():
                assert v == new.get(k)
        else:
            assert old == new

    compareList = [
        # from anoncreds wallet
        (unpersistedWallet.walletId, restoredWallet.walletId),
        (unpersistedWallet._repo.wallet.name, restoredWallet._repo.wallet.name),

        # from sovrin-issuer-wallet-in-memory
        (unpersistedWallet.availableClaimsToAll, restoredWallet.availableClaimsToAll),
        (unpersistedWallet.availableClaimsByNonce, restoredWallet.availableClaimsByNonce),
        (unpersistedWallet.availableClaimsByIdentifier, restoredWallet.availableClaimsByIdentifier),
        (unpersistedWallet._proofRequestsSchema, restoredWallet._proofRequestsSchema),

        # from anoncreds issuer-wallet-in-memory
        (unpersistedWallet._sks, restoredWallet._sks),
        (unpersistedWallet._skRs, restoredWallet._skRs),
        (unpersistedWallet._accumSks, restoredWallet._accumSks),
        (unpersistedWallet._m2s, restoredWallet._m2s),
        (unpersistedWallet._attributes, restoredWallet._attributes),

        # from anoncreds wallet-in-memory
        (unpersistedWallet._schemasByKey, restoredWallet._schemasByKey),
        (unpersistedWallet._schemasById, restoredWallet._schemasById),
        (unpersistedWallet._pks, restoredWallet._pks),
        (unpersistedWallet._pkRs, restoredWallet._pkRs),
        (unpersistedWallet._accums, restoredWallet._accums),
        (unpersistedWallet._accumPks, restoredWallet._accumPks),
        # TODO: need to check for _tails, it is little bit different than
        # others (Dict instead of namedTuple or class)
    ]

    assert unpersistedWallet._repo.client is None
    assert restoredWallet._repo.client is not None
    for oldDict, newDict in compareList:
        compare(oldDict, newDict)