import json
from _sha256 import sha256
from contextlib import contextmanager
import pytest
from common.serializers.serialization import serialize_msg_for_signing
from indy_common.authorize.auth_actions import EDIT_PREFIX, ADD_PREFIX
from indy_common.authorize.auth_constraints import AuthConstraint
from indy_node.test.attrib_txn.test_send_get_attr import secretBox
from indy_node.test.helper import sdk_send_and_check_auth_rule_request

from plenum.common.constants import STEWARD_STRING, STEWARD
from plenum.common.exceptions import RequestRejectedException
from plenum.common.util import adict, randomString
from indy_common.constants import ENDORSER_STRING, ATTRIB
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
                            sdk_wallet_endorser, attributeData, looper):
    _, did_cl = sdk_user_wallet_a
    req_couple = sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, attributeData, did_cl)[0]
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


def testEndorserAddsAttributeForUser(sdk_added_raw_attribute):
    pass


def testEndorserGetAttrsForUser(looper,
                                   sdk_user_wallet_a,
                                   sdk_wallet_endorser,
                                   sdk_pool_handle,
                                   attributeName,
                                   sdk_added_raw_attribute):
    _, dest = sdk_user_wallet_a
    sdk_get_attribute_and_check(looper, sdk_pool_handle,
                                sdk_wallet_endorser, dest, attributeName)


def test_edit_attrib(sdk_pool_handle, sdk_user_wallet_a,
                     sdk_wallet_endorser, attributeData, looper, attributeName):
    _, did_cl = sdk_user_wallet_a

    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, attributeData, did_cl)
    res1 = sdk_get_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, did_cl, attributeName)
    assert serialize_msg_for_signing(
        json.loads(res1[0][1]['result']['data'])) == serialize_msg_for_signing(
        json.loads(attributeData.replace(' ', '')))

    data = json.loads(attributeData)
    data[attributeName] = {'John': 'Snow'}
    data = json.dumps(data)

    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, data, did_cl)
    res2 = sdk_get_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, did_cl, attributeName)
    assert serialize_msg_for_signing(
        json.loads(res2[0][1]['result']['data'])) == serialize_msg_for_signing(
        json.loads(data.replace(' ', '')))


def test_non_endorser_cannot_add_attribute_for_user(
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
    e.match('can not touch raw field since only the owner can modify it')


def testOnlyUsersEndorserCanAddAttribute(
        nodeSet,
        looper,
        attributeData,
        sdk_pool_handle,
        sdk_wallet_trustee,
        sdk_user_wallet_a):
    _, dest = sdk_user_wallet_a
    wallet_another_ta = sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee,
                                        alias='TA-' + randomString(5), role=ENDORSER_STRING)
    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle,
                                    wallet_another_ta, attributeData, dest)
    e.match('can not touch raw field since only the owner can modify it')


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
    e.match('can not touch raw field since only the owner can modify it')


# TODO: Ask Jason, if getting the latest attribute makes sense since in case
# of encrypted and hashed attributes, there is no name.
def testLatestAttrIsReceived(
        looper,
        nodeSet,
        sdk_wallet_endorser,
        sdk_pool_handle,
        sdk_user_wallet_a):
    _, dest = sdk_user_wallet_a

    attr1 = json.dumps({'name': 'Mario'})
    sdk_add_attribute_and_check(looper, sdk_pool_handle,
                                sdk_wallet_endorser, attr1, dest)
    reply = sdk_get_attribute_and_check(looper, sdk_pool_handle,
                                        sdk_wallet_endorser, dest, 'name')[0]
    reply_equality_of_get_attribute(reply, 'Mario')

    attr2 = json.dumps({'name': 'Luigi'})
    sdk_add_attribute_and_check(looper, sdk_pool_handle,
                                sdk_wallet_endorser, attr2, dest)
    reply = sdk_get_attribute_and_check(looper, sdk_pool_handle,
                                        sdk_wallet_endorser, dest, 'name')[0]
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
    #           endorser,
    #           addedEndorser,
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
def testGetTxnsSeqNo(nodeSet, endorserWallet, looper):
    pass
    """
    Test GET_TXNS from client and provide seqNo to fetch from
    """
    # looper.add(endorser)
    # looper.run(endorser.ensureConnectedToNodes())
    #
    # def chk():
    #     assert endorser.spylog.count(
    #         endorser.requestPendingTxns.__name__) > 0
    #
    # # TODO choose or create timeout in 'waits' on this case.
    # looper.run(eventually(chk, retryWait=1, timeout=3))


@pytest.mark.skip(reason="SOV-560. Attribute encryption is done in client")
def testEndorserAddedAttributeIsEncrypted(addedEncryptedAttribute):
    pass


@pytest.mark.skip(reason="SOV-560. Attribute Disclosure is not done for now")
def testEndorserDisclosesEncryptedAttribute(
        addedEncryptedAttribute,
        symEncData,
        looper,
        userSignerA,
        endorserSigner,
        endorser):
    pass
    # box = libnacl.public.Box(endorserSigner.naclSigner.keyraw,
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
    # submitAndCheck(looper, endorser, op,
    #                identifier=endorserSigner.verstr)


@pytest.mark.skip(reason="SOV-561. Pending implementation")
def testEndorserAddedAttributeCanBeChanged(sdk_added_raw_attribute):
    # TODO but only by user(if user has taken control of his identity) and
    # endorser
    raise NotImplementedError


def set_attrib_auth_to_none(looper, sdk_wallet_trustee, sdk_pool_handle):
    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=ADD_PREFIX,
                                         auth_type=ATTRIB,
                                         field='*',
                                         new_value='*',
                                         constraint=AuthConstraint(role='*', sig_count=1,
                                                                   need_to_be_owner=True).as_dict)

    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=EDIT_PREFIX,
                                         auth_type=ATTRIB,
                                         field='*',
                                         new_value='*',
                                         old_value='*',
                                         constraint=AuthConstraint(role='*', sig_count=1,
                                                                   need_to_be_owner=True).as_dict)


def test_auth_rule_for_raw_attrib_works(looper,
                                        sdk_wallet_trustee,
                                        sdk_pool_handle,
                                        sdk_user_wallet_a,
                                        sdk_wallet_endorser):
    _, did_cl = sdk_user_wallet_a

    # We can add and modify attribs
    data = dict()
    data['a'] = {'John': 'Snow'}
    data = json.dumps(data)
    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, data, did_cl)

    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, data, did_cl)

    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=EDIT_PREFIX,
                                         auth_type=ATTRIB,
                                         field='*',
                                         new_value='*',
                                         old_value='*',
                                         constraint=AuthConstraint(role=STEWARD, sig_count=1).as_dict)

    # We still can add, but cannot edit attrib
    data = dict()
    data['b'] = {'John': 'Snow'}
    data = json.dumps(data)
    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, data, did_cl)

    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, data, did_cl)
    e.match('Not enough STEWARD signatures')

    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=ADD_PREFIX,
                                         auth_type=ATTRIB,
                                         field='*',
                                         new_value='*',
                                         constraint=AuthConstraint(role=STEWARD, sig_count=1).as_dict)
    # We cannot add or edit attrib
    data = dict()
    data['c'] = {'John': 'Snow'}
    data = json.dumps(data)
    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, data, did_cl)
    e.match('Not enough STEWARD signatures')

    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, data, did_cl)
    e.match('Not enough STEWARD signatures')


def test_auth_rule_for_hash_attrib_works(looper,
                                         sdk_wallet_trustee,
                                         sdk_pool_handle,
                                         sdk_user_wallet_a,
                                         sdk_wallet_endorser):
    _, did_cl = sdk_user_wallet_a

    set_attrib_auth_to_none(looper, sdk_wallet_trustee, sdk_pool_handle)

    # We can add and modify attribs
    data = sha256(json.dumps({'name': 'John'}).encode()).hexdigest()
    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, None, did_cl, xhash=data)

    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, None, did_cl, xhash=data)

    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=EDIT_PREFIX,
                                         auth_type=ATTRIB,
                                         field='*',
                                         new_value='*',
                                         old_value='*',
                                         constraint=AuthConstraint(role=STEWARD, sig_count=1).as_dict)

    # We still can add, but cannot edit attrib
    data = sha256(json.dumps({'name': 'Ned'}).encode()).hexdigest()

    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, None, did_cl, xhash=data)

    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, None, did_cl, xhash=data)
    e.match('Not enough STEWARD signatures')

    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=ADD_PREFIX,
                                         auth_type=ATTRIB,
                                         field='*',
                                         new_value='*',
                                         constraint=AuthConstraint(role=STEWARD, sig_count=1).as_dict)
    # We cannot add or edit attrib
    data = sha256(json.dumps({'name': 'Aria'}).encode()).hexdigest()

    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, None, did_cl, xhash=data)
    e.match('Not enough STEWARD signatures')

    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, None, did_cl, xhash=data)
    e.match('Not enough STEWARD signatures')


def test_auth_rule_for_enc_attrib_works(looper,
                                        sdk_wallet_trustee,
                                        sdk_pool_handle,
                                        sdk_user_wallet_a,
                                        sdk_wallet_endorser):
    _, did_cl = sdk_user_wallet_a

    set_attrib_auth_to_none(looper, sdk_wallet_trustee, sdk_pool_handle)

    # We can add and modify attribs
    data = secretBox.encrypt(json.dumps({'name': 'Jaime'}).encode()).hex()
    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, None, did_cl, enc=data)

    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, None, did_cl, enc=data)

    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=EDIT_PREFIX,
                                         auth_type=ATTRIB,
                                         field='*',
                                         new_value='*',
                                         old_value='*',
                                         constraint=AuthConstraint(role=STEWARD, sig_count=1).as_dict)

    # We still can add, but cannot edit attrib
    data = secretBox.encrypt(json.dumps({'name': 'Cersei'}).encode()).hex()

    sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, None, did_cl, enc=data)

    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, None, did_cl, enc=data)
    e.match('Not enough STEWARD signatures')

    sdk_send_and_check_auth_rule_request(looper,
                                         sdk_pool_handle,
                                         sdk_wallet_trustee,
                                         auth_action=ADD_PREFIX,
                                         auth_type=ATTRIB,
                                         field='*',
                                         new_value='*',
                                         constraint=AuthConstraint(role=STEWARD, sig_count=1).as_dict)
    # We cannot add or edit attrib
    data = secretBox.encrypt(json.dumps({'name': 'Tywin'}).encode()).hex()

    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, None, did_cl, enc=data)
    e.match('Not enough STEWARD signatures')

    with pytest.raises(RequestRejectedException) as e:
        sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, None, did_cl, enc=data)
    e.match('Not enough STEWARD signatures')
