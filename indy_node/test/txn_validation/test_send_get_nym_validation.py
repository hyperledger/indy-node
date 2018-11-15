from binascii import hexlify
import pytest

from indy.ledger import build_get_nym_request
from indy_common.constants import TRUST_ANCHOR_STRING
from indy_node.test.helper import check_str_is_base58_compatible, modify_field, \
    createUuidIdentifier, createHalfKeyIdentifierAndAbbrevVerkey, createCryptonym
from indy_node.test.nym_txn.test_nym_additional import get_nym

from plenum.test.helper import sdk_get_and_check_replies
from plenum.common.util import friendlyToRaw
from plenum.common.exceptions import RequestNackedException
from plenum.common.constants import IDENTIFIER
from plenum.test.pool_transactions.helper import sdk_add_new_nym, sdk_sign_and_send_prepared_request


def testSendGetNymSucceedsForExistingUuidDest(
        looper, sdk_pool_handle, sdk_wallet_trustee):
    new_wallet = sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee)
    get_nym(looper, sdk_pool_handle, sdk_wallet_trustee, new_wallet[1])


def testSendGetNymFailsForNotExistingUuidDest(
        looper, sdk_pool_handle, sdk_wallet_trustee):
    get_nym(looper, sdk_pool_handle, sdk_wallet_trustee, createUuidIdentifier())


def test_get_nym_returns_role(
        looper, sdk_pool_handle, sdk_wallet_trustee):
    current_role = TRUST_ANCHOR_STRING
    uuidIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee,
                    dest=uuidIdentifier, verkey=abbrevVerkey, role=current_role)
    get_nym(looper, sdk_pool_handle, sdk_wallet_trustee, createUuidIdentifier())

    new_role = ''
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee,
                    dest=uuidIdentifier, verkey=abbrevVerkey, role=new_role)
    get_nym(looper, sdk_pool_handle, sdk_wallet_trustee, createUuidIdentifier())


def testSendGetNymFailsIfCryptonymIsPassedAsDest(
        looper, sdk_pool_handle, sdk_wallet_trustee):
    get_nym(looper, sdk_pool_handle, sdk_wallet_trustee, createCryptonym())


def testSendGetNymFailsIfDestIsPassedInHexFormat(
        looper, sdk_pool_handle, sdk_wallet_trustee):
    # Sometimes hex representation can use only base58 compatible characters
    while True:
        uuidIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
        hexEncodedUuidIdentifier = hexlify(
            friendlyToRaw(uuidIdentifier)).decode()
        if not check_str_is_base58_compatible(hexEncodedUuidIdentifier):
            break
    sdk_add_new_nym(looper, sdk_pool_handle, sdk_wallet_trustee, dest=uuidIdentifier, verkey=abbrevVerkey)

    _, s_did = sdk_wallet_trustee
    get_nym_req = looper.loop.run_until_complete(build_get_nym_request(s_did, uuidIdentifier))
    get_nym_req = modify_field(get_nym_req, hexEncodedUuidIdentifier, IDENTIFIER)
    req = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                             sdk_pool_handle, get_nym_req)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [req])
    e.match('should not contain the following chars')


def testSendGetNymFailsIfDestIsInvalid(
        looper, sdk_pool_handle, sdk_wallet_trustee):
    uuidIdentifier = createUuidIdentifier()
    invalidIdentifier = uuidIdentifier[:-4]
    _, s_did = sdk_wallet_trustee
    get_nym_req = looper.loop.run_until_complete(build_get_nym_request(s_did, uuidIdentifier))
    get_nym_req = modify_field(get_nym_req, invalidIdentifier, IDENTIFIER)
    req = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                             sdk_pool_handle, get_nym_req)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [req])
    e.match('should be one of \[16, 32\]')


def testSendGetNymHasInvalidSyntaxIfDestIsEmpty(
        looper, sdk_pool_handle, sdk_wallet_trustee):
    uuidIdentifier = createUuidIdentifier()
    _, s_did = sdk_wallet_trustee
    get_nym_req = looper.loop.run_until_complete(build_get_nym_request(s_did, uuidIdentifier))
    get_nym_req = modify_field(get_nym_req, '', IDENTIFIER)
    req = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                             sdk_pool_handle, get_nym_req)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [req])
    e.match('client request invalid')
