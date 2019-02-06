import json
from contextlib import contextmanager
import pytest

from plenum.common.constants import STEWARD_STRING
from plenum.common.exceptions import RequestRejectedException
from plenum.common.util import adict, randomString
from indy_common.constants import TRUST_ANCHOR_STRING
from indy_common.util import getSymmetricallyEncryptedVal
from indy_node.test.helper import sdk_add_attribute_and_check, sdk_get_attribute_and_check
from plenum.test.pool_transactions.helper import sdk_add_new_nym
from stp_core.common.log import getlogger

logger = getlogger()


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
def sdk_added_raw_attribute(sdk_pool_handle, sdk_user_wallet_a,
                            sdk_wallet_trust_anchor, attributeData, looper):
    _, did_cl = sdk_user_wallet_a
    req_couple = sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_trust_anchor, attributeData, did_cl)[0]
    return req_couple[1]


@pytest.fixture(scope="module")
def symEncData(attributeData):
    encData, secretKey = getSymmetricallyEncryptedVal(attributeData)
    return adict(data=attributeData, encData=encData, secretKey=secretKey)


@contextmanager
def whitelistextras(*msg):
    global whitelistArray
    ins = {m: (m in whitelistArray) for m in msg}
    [whitelistArray.append(m) for m, _in in ins.items() if not _in]
    yield
    [whitelistArray.remove(m) for m, _in in ins.items() if not _in]


def testTrustAnchorAddsAttributeForUser(sdk_added_raw_attribute):
    pass


def testTrustAnchorGetAttrsForUser(looper,
                                   sdk_user_wallet_a,
                                   sdk_wallet_trust_anchor,
                                   sdk_pool_handle,
                                   attributeName,
                                   sdk_added_raw_attribute):
    _, dest = sdk_user_wallet_a
    sdk_get_attribute_and_check(looper, sdk_pool_handle,
                                sdk_wallet_trust_anchor, dest, attributeName)


def test_non_trust_anchor_cannot_add_attribute_for_user(
        looper,
        nodeSet,
        sdk_wallet_client,
        sdk_pool_handle,
        sdk_user_wallet_a,
        attributeData):
    _, dest = sdk_user_wallet_a

    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle,
                                    sdk_wallet_client, attributeData, dest)
    e.match('Only identity owner/guardian can add attribute for that identity')


def testOnlyUsersTrustAnchorCanAddAttribute(
        nodeSet,
        looper,
        attributeData,
        sdk_pool_handle,
        sdk_wallet_trustee,
        sdk_user_wallet_a):
    _, dest = sdk_user_wallet_a
    wallet_another_ta = sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee,
                                        alias='TA-' + randomString(5), role=TRUST_ANCHOR_STRING)
    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle,
                                    wallet_another_ta, attributeData, dest)
    e.match('Only identity owner/guardian can add attribute for that identity')


def testStewardCannotAddUsersAttribute(
        nodeSet,
        looper,
        attributeData,
        sdk_pool_handle,
        sdk_wallet_trustee,
        sdk_user_wallet_a):
    _, dest = sdk_user_wallet_a
    wallet_another_stewatd = sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee,
                                             alias='TA-' + randomString(5), role=STEWARD_STRING)
    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle,
                                    wallet_another_stewatd, attributeData, dest)
    e.match('Only identity owner/guardian can add attribute for that identity')


# TODO: Ask Jason, if getting the latest attribute makes sense since in case
# of encrypted and hashed attributes, there is no name.
def testLatestAttrIsReceived(
        looper,
        nodeSet,
        sdk_wallet_trust_anchor,
        sdk_pool_handle,
        sdk_user_wallet_a):
    _, dest = sdk_user_wallet_a

    attr1 = json.dumps({'name': 'Mario'})
    sdk_add_attribute_and_check(looper, sdk_pool_handle,
                                sdk_wallet_trust_anchor, attr1, dest)
    reply = sdk_get_attribute_and_check(looper, sdk_pool_handle,
                                        sdk_wallet_trust_anchor, dest, 'name')[0]
    reply_equality_of_get_attribute(reply, 'Mario')

    attr2 = json.dumps({'name': 'Luigi'})
    sdk_add_attribute_and_check(looper, sdk_pool_handle,
                                sdk_wallet_trust_anchor, attr2, dest)
    reply = sdk_get_attribute_and_check(looper, sdk_pool_handle,
                                        sdk_wallet_trust_anchor, dest, 'name')[0]
    reply_equality_of_get_attribute(reply, 'Luigi')


def reply_equality_of_get_attribute(reply, value):
    result = reply[1]['result']
    assert json.loads(result['data'])[result['raw']] == value


def test_user_add_attrs_for_herself_and_get_it(
        looper,
        nodeSet,
        sdk_wallet_trustee,
        sdk_pool_handle):
    wallet_client = sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee, role=None)
    _, dest = wallet_client
    attr = json.dumps({'name': 'Albus'})
    sdk_add_attribute_and_check(looper, sdk_pool_handle,
                                wallet_client, attr, dest)
    sdk_get_attribute_and_check(looper, sdk_pool_handle,
                                wallet_client, dest, 'name')


@pytest.mark.skip(reason="INDY-896 ATTR cannot be added without dest")
def test_attr_with_no_dest_added(nodeSet, looper, attributeData):
    pass
    # user_wallet = Wallet()
    # signer = DidSigner()
    # user_wallet.addIdentifier(signer=signer)
    #
    # client.registerObserver(user_wallet.handleIncomingReply)
    # looper.add(client)
    # looper.run(client.ensureConnectedToNodes())
    # makePendingTxnsRequest(client, user_wallet)
    #
    # createNym(looper,
    #           user_wallet.defaultId,
    #           trustAnchor,
    #           addedTrustAnchor,
    #           role=None,
    #           verkey=user_wallet.getVerkey())
    #
    # attr1 = json.dumps({'age': "24"})
    # attrib = Attribute(name='test4 attribute',
    #                    origin=user_wallet.defaultId,
    #                    value=attr1,
    #                    dest=None,
    #                    ledgerStore=LedgerStore.RAW)
    # addAttributeAndCheck(looper, client, user_wallet, attrib)


@pytest.mark.skip(reason="SOV-561. Test not implemented")
def testGetTxnsNoSeqNo():
    """
    Test GET_TXNS from client and do not provide any seqNo to fetch from
    """
    raise NotImplementedError


@pytest.mark.skip(reason="SOV-560. Come back to it later since "
                         "requestPendingTxns move to wallet")
def testGetTxnsSeqNo(nodeSet, trustAnchorWallet, looper):
    pass
    """
    Test GET_TXNS from client and provide seqNo to fetch from
    """
    # looper.add(trustAnchor)
    # looper.run(trustAnchor.ensureConnectedToNodes())
    #
    # def chk():
    #     assert trustAnchor.spylog.count(
    #         trustAnchor.requestPendingTxns.__name__) > 0
    #
    # # TODO choose or create timeout in 'waits' on this case.
    # looper.run(eventually(chk, retryWait=1, timeout=3))


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
    pass
    # box = libnacl.public.Box(trustAnchorSigner.naclSigner.keyraw,
    #                          userSignerA.naclSigner.verraw)
    #
    # data = json.dumps({SKEY: symEncData.secretKey,
    #                    TXN_ID: addedEncryptedAttribute[TXN_ID]})
    # nonce, boxedMsg = box.encrypt(data.encode(), pack_nonce=False)
    #
    # op = {
    #     TARGET_NYM: userSignerA.verstr,
    #     TXN_TYPE: ATTRIB,
    #     NONCE: base58.b58encode(nonce).decode("utf-8"),
    #     ENC: base58.b58encode(boxedMsg).decode("utf-8")
    # }
    # submitAndCheck(looper, trustAnchor, op,
    #                identifier=trustAnchorSigner.verstr)


@pytest.mark.skip(reason="SOV-561. Pending implementation")
def testTrustAnchorAddedAttributeCanBeChanged(sdk_added_raw_attribute):
    # TODO but only by user(if user has taken control of his identity) and
    # trustAnchor
    raise NotImplementedError
