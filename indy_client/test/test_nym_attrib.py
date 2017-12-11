import json
from contextlib import contextmanager

import base58
import libnacl.public
import pytest

from plenum.common.constants import ENC, REPLY, TXN_TIME, TXN_ID, \
    OP_FIELD_NAME, NYM, TARGET_NYM, \
    TXN_TYPE, ROLE, NONCE, VERKEY
from plenum.common.signer_did import DidSigner
from plenum.common.types import f
from plenum.common.util import adict
from plenum.test import waits
from indy_client.client.client import Client
from indy_client.client.wallet.attribute import Attribute, LedgerStore
from indy_client.client.wallet.wallet import Wallet
from indy_client.test.helper import checkNacks, submitAndCheckRejects, \
    genTestClient, createNym, checkRejects, makePendingTxnsRequest
from indy_common.constants import SKEY
from indy_common.identity import Identity
from indy_common.txn_util import ATTRIB, TRUST_ANCHOR
from indy_common.util import getSymmetricallyEncryptedVal
from indy_node.test.helper import submitAndCheck, \
    makeAttribRequest, makeGetNymRequest, addAttributeAndCheck, TestNode, \
    getAttribute
from stp_core.common.log import getlogger
from stp_core.loop.eventually import eventually


logger = getlogger()

whitelistArray = []


def whitelist():
    return whitelistArray


@pytest.fixture(scope="module")
def attributeName():
    return 'endpoint'


@pytest.fixture(scope="module")
def attributeValue():
    return {
        "ha": "127.0.0.1:9700",
        "verkey": "F46i9NmUN72QMbbm5qWetB6CmfT7hiU8BM1qrtTGLKsc"
    }


@pytest.fixture(scope="module")
def attributeData(attributeName, attributeValue):
    return json.dumps({attributeName: attributeValue})


@pytest.fixture(scope="module")
def addedRawAttribute(userWalletA: Wallet, trustAnchor: Client,
                      trustAnchorWallet: Wallet, attributeData, looper):
    attrib = Attribute(name='test attribute',
                       origin=trustAnchorWallet.defaultId,
                       value=attributeData,
                       dest=userWalletA.defaultId,
                       ledgerStore=LedgerStore.RAW)
    addAttributeAndCheck(looper, trustAnchor, trustAnchorWallet, attrib)
    return attrib


@pytest.fixture(scope="module")
def symEncData(attributeData):
    encData, secretKey = getSymmetricallyEncryptedVal(attributeData)
    return adict(data=attributeData, encData=encData, secretKey=secretKey)


@pytest.fixture(scope="module")
def addedEncryptedAttribute(userIdA, trustAnchor, trustAnchorWallet, looper,
                            symEncData):
    op = {
        TARGET_NYM: userIdA,
        TXN_TYPE: ATTRIB,
        ENC: symEncData.encData
    }

    return submitAndCheck(looper, trustAnchor, trustAnchorWallet, op)[0]


@pytest.fixture(scope="module")
def nonTrustAnchor(looper, nodeSet, tdirWithClientPoolTxns):
    sseed = b'a secret trust anchor seed......'
    signer = DidSigner(seed=sseed)
    c, _ = genTestClient(nodeSet, tmpdir=tdirWithClientPoolTxns, usePoolLedger=True)
    w = Wallet(c.name)
    w.addIdentifier(signer=signer)
    c.registerObserver(w.handleIncomingReply)
    looper.add(c)
    looper.run(c.ensureConnectedToNodes())
    return c, w


@pytest.fixture(scope="module")
def anotherTrustAnchor(nodeSet, steward, stewardWallet, tdirWithClientPoolTxns, looper):
    sseed = b'1 secret trust anchor seed......'
    signer = DidSigner(seed=sseed)
    c, _ = genTestClient(nodeSet, tmpdir=tdirWithClientPoolTxns, usePoolLedger=True)
    w = Wallet(c.name)
    w.addIdentifier(signer=signer)
    c.registerObserver(w.handleIncomingReply)
    looper.add(c)
    looper.run(c.ensureConnectedToNodes())
    createNym(looper, signer.identifier, steward, stewardWallet,
              role=TRUST_ANCHOR, verkey=signer.verkey)
    return c, w


def testCreateStewardWallet(stewardWallet):
    pass


@contextmanager
def whitelistextras(*msg):
    global whitelistArray
    ins = {m: (m in whitelistArray) for m in msg}
    [whitelistArray.append(m) for m, _in in ins.items() if not _in]
    yield
    [whitelistArray.remove(m) for m, _in in ins.items() if not _in]


def add_nym_operation(signer=None, seed=None, role=None):
    if signer is None:
        signer = DidSigner(seed=seed)

    op = {
        TARGET_NYM: signer.identifier,
        VERKEY: signer.verkey,
        TXN_TYPE: NYM,
    }

    if role is not None:
        op[ROLE] = role

    return op


def test_non_steward_cannot_create_trust_anchor(
        nodeSet, trustAnchor, addedTrustAnchor, client1, looper):

    with whitelistextras("UnknownIdentifier"):
        non_permission = Wallet()
        signer = DidSigner()
        non_permission.addIdentifier(signer=signer)

        createNym(looper,
                  non_permission.defaultId,
                  trustAnchor,
                  addedTrustAnchor,
                  role=None,
                  verkey=non_permission.getVerkey())

        op = add_nym_operation(
            seed=b'a secret trust anchor seed......', role=TRUST_ANCHOR)

        submitAndCheckRejects(
            looper=looper,
            client=client1,
            wallet=non_permission,
            op=op,
            identifier=non_permission.defaultId,
            contains="UnauthorizedClientRequest")


def testStewardCreatesATrustAnchor(steward, addedTrustAnchor):
    pass


@pytest.mark.skip(
    reason="SOV-560. Cannot create another sponsor with same nym")
def testStewardCreatesAnotherTrustAnchor(
        nodeSet,
        steward,
        stewardWallet,
        looper,
        trustAnchorWallet):
    createNym(looper, trustAnchorWallet.defaultId, steward, stewardWallet,
              TRUST_ANCHOR)
    return trustAnchorWallet


def test_non_trust_anchor_cannot_create_user(
        nodeSet, looper, trustAnchor, addedTrustAnchor, client1):
    with whitelistextras("UnknownIdentifier"):
        non_trust_anchor = Wallet()
        signer = DidSigner()
        non_trust_anchor.addIdentifier(signer=signer)

        createNym(looper,
                  non_trust_anchor.defaultId,
                  trustAnchor,
                  addedTrustAnchor,
                  role=None,
                  verkey=non_trust_anchor.getVerkey())

        op = add_nym_operation(seed=b'a secret trust anchor seed......')

        submitAndCheckRejects(
            looper=looper,
            client=client1,
            wallet=non_trust_anchor,
            op=op,
            identifier=non_trust_anchor.defaultId,
            contains="UnauthorizedClientRequest")


def testTrustAnchorCreatesAUser(steward, userWalletA):
    pass


def test_nym_addition_fails_with_empty_verkey(looper, addedTrustAnchor,
                                              trustAnchor, trustAnchorWallet):

    op = add_nym_operation(seed=b'a secret trust anchor seed......')
    op[VERKEY] = ''
    submitAndCheckRejects(
        looper=looper,
        client=trustAnchor,
        wallet=trustAnchorWallet,
        op=op,
        identifier=trustAnchorWallet.defaultId,
        contains='validation error [ClientNYMOperation]: b58 decoded value length 0 should be one of [32]',
        check_func=checkNacks)


@pytest.fixture(scope="module")
def nymsAddedInQuickSuccession(nodeSet, addedTrustAnchor, looper,
                               trustAnchor, trustAnchorWallet):
    usigner = DidSigner()
    nym = usigner.verkey
    idy = Identity(identifier=nym)
    trustAnchorWallet.addTrustAnchoredIdentity(idy)
    # Creating a NYM request with same nym again
    req = idy.ledgerRequest()
    trustAnchorWallet._pending.appendleft((req, idy.identifier))
    reqs = trustAnchorWallet.preparePending()
    trustAnchor.submitReqs(*reqs)

    def check():
        assert trustAnchorWallet._trustAnchored[nym].seqNo

    timeout = waits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(check, timeout=timeout))

    timeout = waits.expectedReqNAckQuorumTime()
    looper.run(eventually(checkNacks,
                          trustAnchor,
                          req.reqId,
                          "is already added",
                          retryWait=1, timeout=timeout))
    count = 0
    for node in nodeSet:
        for seq, txn in node.domainLedger.getAllTxn():
            if txn[TXN_TYPE] == NYM and txn[TARGET_NYM] == usigner.identifier:
                count += 1

    assert(count == len(nodeSet))


def testTrustAnchorAddsAttributeForUser(addedRawAttribute):
    pass


def testClientGetsResponseWithoutConsensusForUsedReqId(
        nodeSet,
        looper,
        steward,
        addedTrustAnchor,
        trustAnchor,
        userWalletA,
        attributeName,
        attributeData,
        addedRawAttribute):
    lastReqId = None
    replies = {}
    for msg, sender in reversed(trustAnchor.inBox):
        if msg[OP_FIELD_NAME] == REPLY:
            if not lastReqId:
                lastReqId = msg[f.RESULT.nm][f.REQ_ID.nm]
            if msg.get(f.RESULT.nm, {}).get(f.REQ_ID.nm) == lastReqId:
                replies[sender] = msg
            if len(replies) == len(nodeSet):
                break

    trustAnchorWallet = addedTrustAnchor
    attrib = Attribute(name=attributeName,
                       origin=trustAnchorWallet.defaultId,
                       value=attributeData,
                       dest=userWalletA.defaultId,
                       ledgerStore=LedgerStore.RAW)
    trustAnchorWallet.addAttribute(attrib)
    req = trustAnchorWallet.preparePending()[0]
    _, key = trustAnchorWallet._prepared.pop((req.identifier, req.reqId))
    req.reqId = lastReqId

    req.signature = trustAnchorWallet.signMsg(
        msg=req.signingState(identifier=req.identifier),
        identifier=req.identifier)
    trustAnchorWallet._prepared[req.identifier, req.reqId] = req, key
    trustAnchor.submitReqs(req)

    def chk():
        nonlocal trustAnchor, lastReqId, replies
        for node in nodeSet:
            last = node.spylog.getLast(TestNode.getReplyFromLedger.__name__)
            assert last
            result = last.result
            assert result is not None

            replies[node.clientstack.name][f.RESULT.nm].pop(TXN_TIME, None)
            result.result.pop(TXN_TIME, None)

            assert {k: v for k, v in result.result.items() if v is not None}.items() <=\
                   replies[node.clientstack.name][f.RESULT.nm].items()

    timeout = waits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(chk, retryWait=1, timeout=timeout))


@pytest.fixture(scope="module")
def checkAddAttribute(
        userWalletA,
        trustAnchor,
        trustAnchorWallet,
        attributeName,
        attributeValue,
        addedRawAttribute,
        looper):
    getAttribute(looper=looper,
                 trustAnchor=trustAnchor,
                 trustAnchorWallet=trustAnchorWallet,
                 userIdA=userWalletA.defaultId,
                 attributeName=attributeName,
                 attributeValue=attributeValue)


def testTrustAnchorGetAttrsForUser(checkAddAttribute):
    pass


def test_non_trust_anchor_cannot_add_attribute_for_user(
        nodeSet,
        nonTrustAnchor,
        trustAnchor,
        addedTrustAnchor,
        userIdA,
        looper,
        attributeData):
    with whitelistextras('UnauthorizedClientRequest'):
        client, wallet = nonTrustAnchor

        createNym(looper,
                  wallet.defaultId,
                  trustAnchor,
                  addedTrustAnchor,
                  role=None,
                  verkey=wallet.getVerkey())

        attrib = Attribute(name='test1 attribute',
                           origin=wallet.defaultId,
                           value=attributeData,
                           dest=userIdA,
                           ledgerStore=LedgerStore.RAW)
        reqs = makeAttribRequest(client, wallet, attrib)
        timeout = waits.expectedTransactionExecutionTime(len(nodeSet))
        looper.run(
            eventually(
                checkRejects,
                client,
                reqs[0].reqId,
                "UnauthorizedClientRequest('Only identity "
                "owner/guardian can add attribute for that identity'",
                retryWait=1,
                timeout=timeout))


def testOnlyUsersTrustAnchorCanAddAttribute(
        nodeSet,
        looper,
        steward,
        stewardWallet,
        attributeData,
        anotherTrustAnchor,
        userIdA):
    with whitelistextras("UnauthorizedClientRequest"):
        client, wallet = anotherTrustAnchor
        attrib = Attribute(name='test2 attribute',
                           origin=wallet.defaultId,
                           value=attributeData,
                           dest=userIdA,
                           ledgerStore=LedgerStore.RAW)
        reqs = makeAttribRequest(client, wallet, attrib)
        timeout = waits.expectedReqNAckQuorumTime()
        looper.run(
            eventually(
                checkRejects,
                client,
                reqs[0].reqId,
                "UnauthorizedClientRequest('Only identity "
                "owner/guardian can add attribute for that identity'",
                retryWait=1,
                timeout=timeout))


def testStewardCannotAddUsersAttribute(nodeSet, looper, steward,
                                       stewardWallet, userIdA, attributeData):
    with whitelistextras("UnauthorizedClientRequest"):
        attrib = Attribute(name='test3 attribute',
                           origin=stewardWallet.defaultId,
                           value=attributeData,
                           dest=userIdA,
                           ledgerStore=LedgerStore.RAW)
        reqs = makeAttribRequest(steward, stewardWallet, attrib)
        timeout = waits.expectedReqNAckQuorumTime()
        looper.run(
            eventually(
                checkRejects,
                steward,
                reqs[0].reqId,
                "UnauthorizedClientRequest('Only identity owner/guardian can "
                "add attribute for that identity'",
                retryWait=1,
                timeout=timeout))


@pytest.mark.skip(reason="SOV-560. Attribute encryption is done in client")
def testTrustAnchorAddedAttributeIsEncrypted(addedEncryptedAttribute):
    pass


@pytest.mark.skip(reason="SOV-560. Attribute Disclosure is not done for now")
def testTrustAnchorDisclosesEncryptedAttribute(
        addedEncryptedAttribute,
        symEncData,
        looper,
        userSignerA,
        trustAnchorSigner,
        trustAnchor):
    box = libnacl.public.Box(trustAnchorSigner.naclSigner.keyraw,
                             userSignerA.naclSigner.verraw)

    data = json.dumps({SKEY: symEncData.secretKey,
                       TXN_ID: addedEncryptedAttribute[TXN_ID]})
    nonce, boxedMsg = box.encrypt(data.encode(), pack_nonce=False)

    op = {
        TARGET_NYM: userSignerA.verstr,
        TXN_TYPE: ATTRIB,
        NONCE: base58.b58encode(nonce),
        ENC: base58.b58encode(boxedMsg)
    }
    submitAndCheck(looper, trustAnchor, op,
                   identifier=trustAnchorSigner.verstr)


@pytest.mark.skip(reason="SOV-561. Pending implementation")
def testTrustAnchorAddedAttributeCanBeChanged(addedRawAttribute):
    # TODO but only by user(if user has taken control of his identity) and
    # trustAnchor
    raise NotImplementedError


def testGetAttribute(
        nodeSet,
        addedTrustAnchor,
        trustAnchorWallet: Wallet,
        trustAnchor,
        userIdA,
        addedRawAttribute,
        attributeData):
    assert attributeData in [
        a.value for a in trustAnchorWallet.getAttributesForNym(userIdA)]


# TODO: Ask Jason, if getting the latest attribute makes sense since in case
# of encrypted and hashed attributes, there is no name.
def testLatestAttrIsReceived(
        nodeSet,
        addedTrustAnchor,
        trustAnchorWallet,
        looper,
        trustAnchor,
        userIdA):

    attr1 = json.dumps({'name': 'Mario'})
    attrib = Attribute(name='name',
                       origin=trustAnchorWallet.defaultId,
                       value=attr1,
                       dest=userIdA,
                       ledgerStore=LedgerStore.RAW)
    addAttributeAndCheck(looper, trustAnchor, trustAnchorWallet, attrib)
    assert attr1 in [
        a.value for a in trustAnchorWallet.getAttributesForNym(userIdA)]

    attr2 = json.dumps({'name': 'Luigi'})
    attrib = Attribute(name='name',
                       origin=trustAnchorWallet.defaultId,
                       value=attr2,
                       dest=userIdA,
                       ledgerStore=LedgerStore.RAW)
    addAttributeAndCheck(looper, trustAnchor, trustAnchorWallet, attrib)
    logger.debug(
        [a.value for a in trustAnchorWallet.getAttributesForNym(userIdA)])
    assert attr2 in [a.value for a in
                     trustAnchorWallet.getAttributesForNym(userIdA)]


@pytest.mark.skip(reason="SOV-561. Test not implemented")
def testGetTxnsNoSeqNo():
    """
    Test GET_TXNS from client and do not provide any seqNo to fetch from
    """
    raise NotImplementedError


@pytest.mark.skip(reason="SOV-560. Come back to it later since "
                         "requestPendingTxns move to wallet")
def testGetTxnsSeqNo(nodeSet, addedTrustAnchor, tdirWithClientPoolTxns,
                     trustAnchorWallet, looper):
    """
    Test GET_TXNS from client and provide seqNo to fetch from
    """
    trustAnchor = genTestClient(nodeSet, tmpdir=tdirWithClientPoolTxns, usePoolLedger=True)

    looper.add(trustAnchor)
    looper.run(trustAnchor.ensureConnectedToNodes())

    def chk():
        assert trustAnchor.spylog.count(
            trustAnchor.requestPendingTxns.__name__) > 0

    # TODO choose or create timeout in 'waits' on this case.
    looper.run(eventually(chk, retryWait=1, timeout=3))


def testNonTrustAnchoredNymCanDoGetNym(nodeSet, addedTrustAnchor,
                                       trustAnchorWallet, tdirWithClientPoolTxns, looper):
    signer = DidSigner()
    someClient, _ = genTestClient(nodeSet, tmpdir=tdirWithClientPoolTxns, usePoolLedger=True)
    wallet = Wallet(someClient.name)
    wallet.addIdentifier(signer=signer)
    someClient.registerObserver(wallet.handleIncomingReply)
    looper.add(someClient)
    looper.run(someClient.ensureConnectedToNodes())
    needle = trustAnchorWallet.defaultId
    makeGetNymRequest(someClient, wallet, needle)
    timeout = waits.expectedTransactionExecutionTime(len(nodeSet))
    looper.run(eventually(someClient.hasNym, needle,
                          retryWait=1, timeout=timeout))


def test_user_add_attrs_for_herself(
        nodeSet,
        looper,
        userClientA,
        userWalletA,
        userIdA,
        trustAnchor,
        addedTrustAnchor,
        attributeData):
    createNym(looper,
              userWalletA.defaultId,
              trustAnchor,
              addedTrustAnchor,
              role=None,
              verkey=userWalletA.getVerkey())

    attr1 = json.dumps({'age': "25"})
    attrib = Attribute(name='test4 attribute',
                       origin=userIdA,
                       value=attr1,
                       dest=userIdA,
                       ledgerStore=LedgerStore.RAW)
    addAttributeAndCheck(looper, userClientA, userWalletA, attrib)


@pytest.mark.skip(reason="INDY-896 ATTR cannot be added without dest")
def test_attr_with_no_dest_added(nodeSet, tdirWithClientPoolTxns, looper,
                                 trustAnchor, addedTrustAnchor, attributeData):
    user_wallet = Wallet()
    signer = DidSigner()
    user_wallet.addIdentifier(signer=signer)

    client, _ = genTestClient(nodeSet, tmpdir=tdirWithClientPoolTxns, usePoolLedger=True)
    client.registerObserver(user_wallet.handleIncomingReply)
    looper.add(client)
    looper.run(client.ensureConnectedToNodes())
    makePendingTxnsRequest(client, user_wallet)

    createNym(looper,
              user_wallet.defaultId,
              trustAnchor,
              addedTrustAnchor,
              role=None,
              verkey=user_wallet.getVerkey())

    attr1 = json.dumps({'age': "24"})
    attrib = Attribute(name='test4 attribute',
                       origin=user_wallet.defaultId,
                       value=attr1,
                       dest=None,
                       ledgerStore=LedgerStore.RAW)
    addAttributeAndCheck(looper, client, user_wallet, attrib)
