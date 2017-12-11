import inspect
import json
from contextlib import ExitStack
from typing import Iterable
import base58

from plenum.common.constants import REQACK, TXN_ID, DATA
from stp_core.common.log import getlogger
from plenum.common.signer_simple import SimpleSigner
from plenum.common.util import getMaxFailures, runall
from plenum.test.helper import TestNodeSet as PlenumTestNodeSet
from plenum.test.helper import waitForSufficientRepliesForRequests, \
    checkLastClientReqForNode, buildCompletedTxnFromReply
from plenum.test.test_node import checkNodesAreReady, TestNodeCore
from plenum.test.test_node import checkNodesConnected
from plenum.test.testable import spyable
from plenum.test import waits as plenumWaits, waits
from indy_client.client.wallet.attribute import LedgerStore, Attribute
from indy_client.client.wallet.wallet import Wallet
from indy_client.test.helper import genTestClient, genTestClientProvider
from indy_common.constants import ATTRIB, TARGET_NYM, TXN_TYPE, GET_NYM
from indy_common.test.helper import TempStorage
from indy_node.server.node import Node
from indy_node.server.upgrader import Upgrader
from stp_core.loop.eventually import eventually
from stp_core.loop.looper import Looper


logger = getlogger()


class Scenario(ExitStack):
    """
    Test context
    simple container to toss in a dynamic context to streamline testing
    """

    def __init__(self,
                 nodeCount=None,
                 nodeRegistry=None,
                 nodeSet=None,
                 looper=None,
                 tmpdir=None):
        super().__init__()

        self.actor = None  # type: Organization

        if nodeSet is None:
            self.nodes = self.enter_context(TestNodeSet(count=nodeCount,
                                                        nodeReg=nodeRegistry,
                                                        tmpdir=tmpdir))
        else:
            self.nodes = nodeSet
        self.nodeReg = self.nodes.nodeReg
        if looper is None:
            self.looper = self.enter_context(Looper(self.nodes))
        else:
            self.looper = looper
        self.tmpdir = tmpdir
        self.ran = []  # history of what has been run
        self.userId = None
        self.userNym = None
        self.trustAnchor = None
        self.trustAnchorNym = None
        self.agent = None
        self.agentNym = None

    def run(self, *coros):
        new = []
        for c in coros:
            if inspect.isfunction(c) or inspect.ismethod(c):
                new.append(c(self))  # call it with this context
            else:
                new.append(c)
        if new:
            result = self.looper.run(*new)
            self.ran.extend(coros)
            return result

    def ensureRun(self, *coros):
        """
        Ensures the coro gets run, in other words, this method optionally
        runs the coro if it has not already been run in this scenario
        :param coros:
        :return:
        """
        unrun = [c for c in coros if c not in self.ran]
        return self.run(*unrun)

    async def start(self):
        await checkNodesConnected(self.nodes)
        timeout = plenumWaits.expectedPoolStartUpTimeout(len(self.nodes))
        await eventually(checkNodesAreReady,
                         self.nodes,
                         retryWait=.25,
                         timeout=timeout,
                         ratchetSteps=10)

    async def startClient(self, org=None):
        org = org if org else self.actor
        self.looper.add(org.client)
        await org.client.ensureConnectedToNodes()

    def copyOfInBox(self, org=None):
        org = org if org else self.actor
        return org.client.inBox.copy()

    async def checkAcks(self, org=None, count=1, minusInBox=None):
        org = org if org else self.actor
        ib = self.copyOfInBox(org)
        if minusInBox:
            for x in minusInBox:
                ib.remove(x)

        timeout = plenumWaits.expectedReqAckQuorumTime()
        for node in self.nodes:
            await eventually(self.checkInboxForReAck,
                             org.client.name,
                             ib,
                             REQACK,
                             node,
                             count,
                             retryWait=.1,
                             timeout=timeout,
                             ratchetSteps=10)

    @staticmethod
    def checkInboxForReAck(clientName, clientInBox, op, fromNode,
                           expectedCount: int):
        actualCount = sum(
            1 for x in clientInBox
            if x[0]['op'] == op and x[1] == fromNode.clientstack.name)
        assert actualCount == expectedCount

    async def checkReplies(self,
                           reqs,
                           org=None,
                           retryWait=.25,
                           timeout=None,
                           ratchetSteps=10):
        org = org if org else self.actor
        if not isinstance(reqs, Iterable):
            reqs = [reqs]

        nodeCount = sum(1 for _ in self.nodes)
        f = getMaxFailures(nodeCount)
        corogen = (eventually(waitForSufficientRepliesForRequests,
                              org.client.inBox,
                              r.reqId,
                              f,
                              retryWait=retryWait,
                              timeout=timeout,
                              ratchetSteps=ratchetSteps) for r in reqs)

        return await runall(corogen)

    async def send(self, op, org=None):
        org = org if org else self.actor
        req = org.client.submit(op)[0]
        timeout = plenumWaits.expectedTransactionExecutionTime(
            len(self.nodes))
        for node in self.nodes:
            await eventually(checkLastClientReqForNode,
                             node,
                             req,
                             retryWait=1,
                             timeout=timeout)
        return req

    async def sendAndCheckAcks(self, op, count: int = 1, org=None):
        baseline = self.copyOfInBox()  # baseline of client inBox so we can
        # net it out
        req = await self.send(op, org)
        await self.checkAcks(count=count, minusInBox=baseline)
        return req

    def genOrg(self):
        cli = genTestClientProvider(nodes=self.nodes,
                                    nodeReg=self.nodeReg.extractCliNodeReg(),
                                    tmpdir=self.tmpdir)
        return Organization(cli)

    def addAgent(self):
        self.agent = self.genOrg()
        return self.agent

    def addTrustAnchor(self):
        self.trustAnchor = self.genOrg()
        return self.trustAnchor


class Organization:
    def __init__(self, client=None):
        self.client = client
        self.wallet = Wallet(self.client)  # created only once per organization
        self.userWallets = {}  # type: Dict[str, Wallet]

    def removeUserWallet(self, userId: str):
        if userId in self.userWallets:
            del self.userWallets[userId]
        else:
            raise ValueError("No wallet exists for this user id")

    def addTxnsForCompletedRequestsInWallet(self, reqs: Iterable, wallet:
                                            Wallet):
        for req in reqs:
            reply, status = self.client.getReply(req.reqId)
            if status == "CONFIRMED":
                # TODO Figure out the actual implementation of
                # TODO     `buildCompletedTxnFromReply`. This is just a stub
                # TODO     implementation
                txn = buildCompletedTxnFromReply(req, reply)
                # TODO Move this logic in wallet
                if txn['txnType'] == ATTRIB and txn['data'] is not None:
                    attr = list(txn['data'].keys())[0]
                    if attr in wallet.attributeEncKeys:
                        key = wallet.attributeEncKeys.pop(attr)
                        txn['secretKey'] = key
                wallet.addCompletedTxn(txn)


@spyable(methods=[Upgrader.processLedger])
class TestUpgrader(Upgrader):
    pass


# noinspection PyShadowingNames,PyShadowingNames
@spyable(
    methods=[Node.handleOneNodeMsg, Node.processRequest, Node.processOrdered,
             Node.postToClientInBox, Node.postToNodeInBox, "eatTestMsg",
             Node.discard,
             Node.reportSuspiciousNode, Node.reportSuspiciousClient,
             Node.processRequest, Node.processPropagate, Node.propagate,
             Node.forward, Node.send, Node.checkPerformance,
             Node.getReplyFromLedger, Node.no_more_catchups_needed,
             Node.onBatchCreated, Node.onBatchRejected])
class TestNode(TempStorage, TestNodeCore, Node):
    def __init__(self, *args, **kwargs):
        Node.__init__(self, *args, **kwargs)
        TestNodeCore.__init__(self, *args, **kwargs)
        self.cleanupOnStopping = True

    def getUpgrader(self):
        return TestUpgrader(self.id, self.name, self.dataLocation, self.config,
                            self.configLedger)

    def getDomainReqHandler(self):
        return Node.getDomainReqHandler(self)

    def init_core_authenticator(self):
        return Node.init_core_authenticator(self)

    def onStopping(self, *args, **kwargs):
        # self.graphStore.store.close()
        super().onStopping(*args, **kwargs)
        if self.cleanupOnStopping:
            self.cleanupDataLocation()


class TestNodeSet(PlenumTestNodeSet):
    def __init__(self,
                 names: Iterable[str] = None,
                 count: int = None,
                 nodeReg=None,
                 tmpdir=None,
                 keyshare=True,
                 primaryDecider=None,
                 pluginPaths: Iterable[str] = None,
                 testNodeClass=TestNode):
        super().__init__(names, count, nodeReg, tmpdir, keyshare,
                         primaryDecider=primaryDecider,
                         pluginPaths=pluginPaths,
                         testNodeClass=testNodeClass)


def checkSubmitted(looper, client, optype, txnsBefore):
    txnsAfter = []

    def checkTxnCountAdvanced():
        nonlocal txnsAfter
        txnsAfter = client.getTxnsByType(optype)
        logger.debug("old and new txns {} {}".format(txnsBefore, txnsAfter))
        assert len(txnsAfter) > len(txnsBefore)

    timeout = plenumWaits.expectedReqAckQuorumTime()
    looper.run(eventually(checkTxnCountAdvanced, retryWait=1,
                          timeout=timeout))
    txnIdsBefore = [txn[TXN_ID] for txn in txnsBefore]
    txnIdsAfter = [txn[TXN_ID] for txn in txnsAfter]
    logger.debug("old and new txnids {} {}".format(txnIdsBefore, txnIdsAfter))
    return list(set(txnIdsAfter) - set(txnIdsBefore))


def submitAndCheck(looper, client, wallet, op, identifier=None):
    # TODO: This assumes every transaction will have an edge in graph, why?
    # Fix this
    optype = op[TXN_TYPE]
    txnsBefore = client.getTxnsByType(optype)
    req = wallet.signOp(op, identifier=identifier)
    wallet.pendRequest(req)
    reqs = wallet.preparePending()
    client.submitReqs(*reqs)
    return checkSubmitted(looper, client, optype, txnsBefore)


def makePendingTxnsRequest(client, wallet):
    wallet.pendSyncRequests()
    prepared = wallet.preparePending()
    client.submitReqs(*prepared)


def makeGetNymRequest(client, wallet, nym):
    op = {
        TARGET_NYM: nym,
        TXN_TYPE: GET_NYM,
    }
    req = wallet.signOp(op)
    # TODO: This looks boilerplate
    wallet.pendRequest(req)
    reqs = wallet.preparePending()
    return client.submitReqs(*reqs)[0]


def makeAttribRequest(client, wallet, attrib):
    wallet.addAttribute(attrib)
    # TODO: This looks boilerplate
    reqs = wallet.preparePending()
    return client.submitReqs(*reqs)[0]


def _newWallet(name=None):
    signer = SimpleSigner()
    w = Wallet(name or signer.identifier)
    w.addIdentifier(signer=signer)
    return w


def addAttributeAndCheck(looper, client, wallet, attrib):
    old = wallet.pendingCount
    pending = wallet.addAttribute(attrib)
    assert pending == old + 1
    reqs = wallet.preparePending()
    client.submitReqs(*reqs)

    def chk():
        assert wallet.getAttribute(attrib).seqNo is not None

    timeout = plenumWaits.expectedTransactionExecutionTime(client.totalNodes)
    looper.run(eventually(chk, retryWait=1, timeout=timeout))
    return wallet.getAttribute(attrib).seqNo


def addRawAttribute(looper, client, wallet, name, value, dest=None,
                    localName=None):
    if not localName:
        localName = name
    attrData = json.dumps({name: value})
    attrib = Attribute(name=localName,
                       origin=wallet.defaultId,
                       value=attrData,
                       dest=wallet.defaultId,
                       ledgerStore=LedgerStore.RAW)
    addAttributeAndCheck(looper, client, wallet, attrib)


def checkGetAttr(reqKey, trustAnchor, attrName, attrValue):
    reply, status = trustAnchor.getReply(*reqKey)
    assert reply
    data = json.loads(reply.get(DATA))
    assert status == "CONFIRMED" and \
        (data is not None and data.get(attrName) == attrValue)
    return reply


def getAttribute(
        looper,
        trustAnchor,
        trustAnchorWallet,
        userIdA,
        attributeName,
        attributeValue):
    # Should be renamed to get_attribute_and_check
    attrib = Attribute(name=attributeName,
                       value=None,
                       dest=userIdA,
                       ledgerStore=LedgerStore.RAW)
    req = trustAnchorWallet.requestAttribute(
        attrib, sender=trustAnchorWallet.defaultId)
    trustAnchor.submitReqs(req)
    timeout = waits.expectedTransactionExecutionTime(len(trustAnchor.nodeReg))
    return looper.run(eventually(checkGetAttr, req.key, trustAnchor,
                                 attributeName, attributeValue, retryWait=1,
                                 timeout=timeout))


def buildStewardClient(looper, tdir, stewardWallet):
    s, _ = genTestClient(tmpdir=tdir, usePoolLedger=True)
    s.registerObserver(stewardWallet.handleIncomingReply)
    looper.add(s)
    looper.run(s.ensureConnectedToNodes())
    makePendingTxnsRequest(s, stewardWallet)
    return s


base58_alphabet = set(base58.alphabet)


def check_str_is_base58_compatible(str):
    return not (set(str) - base58_alphabet)
