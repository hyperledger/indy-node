import json

import pytest

from libnacl import randombytes
from plenum.common.exceptions import RequestNackedException

from plenum.common.constants import TRUSTEE, STEWARD, ROLE
from indy_common.constants import ENDORSER
from plenum.common.types import OPERATION
from plenum.common.util import randomString, hexToFriendly, friendlyToHex, rawToFriendly, friendlyToHexStr

from plenum.test.helper import sdk_get_and_check_replies, sdk_get_bad_response
from indy_node.test.helper import createUuidIdentifier, createHalfKeyIdentifierAndAbbrevVerkey, createCryptonym, \
    createUuidIdentifierAndFullVerkey
from plenum.test.pool_transactions.helper import prepare_nym_request, sdk_sign_and_send_prepared_request


@pytest.fixture(scope='module')
def nym_request(looper, sdk_wallet_trustee):
    seed = randomString(32)
    alias = randomString(5)
    dest = None
    role = None
    verkey = None
    nym_request, _ = looper.loop.run_until_complete(
        prepare_nym_request(sdk_wallet_trustee, seed,
                            alias, role, dest, verkey, True))
    return json.loads(nym_request)


def testSendNymSucceedsForUuidIdentifierAnsdk_pool_handlemittedVerkey(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    parameters = {
        'dest': createUuidIdentifier(),
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


def testSendNymSucceedsForUuidIdentifierAndFullVerkey(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()
    parameters = {
        'dest': uuidIdentifier,
        'verkey': fullVerkey,
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


def testSendNymSucceedsForHalfKeyIdentifierAndAbbrevVerkey(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='INDY-210')
def testSendNymFailsForCryptonymIdentifierAnsdk_pool_handlemittedVerkey(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    parameters = {
        'dest': createCryptonym(),
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='INDY-210')
def testSendNymFailsForCryptonymIdentifierAndFullVerkey(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    cryptonym = createCryptonym()

    _, fullVerkey = createUuidIdentifierAndFullVerkey()
    parameters = {
        'dest': cryptonym,
        'verkey': fullVerkey,
        'role': ENDORSER
    }

    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


def testSendNymFailsForCryptonymIdentifierAndMatchedAbbrevVerkey(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    cryptonym = createCryptonym()

    hexCryptonym = friendlyToHex(cryptonym)
    abbrevVerkey = '~' + hexToFriendly(hexCryptonym[16:])
    parameters = {
        'dest': cryptonym,
        'verkey': abbrevVerkey,
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'Neither a full verkey nor an abbreviated one')


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfIdentifierSizeIs15Bytes(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    parameters = {
        'dest': rawToFriendly(randombytes(15)),
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException, '')


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfIdentifierSizeIs17Bytes(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    parameters = {
        'dest': rawToFriendly(randombytes(17)),
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfFullVerkeySizeIs31Bytes(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    parameters = {
        'dest': rawToFriendly(randombytes(16)),
        'verkey': rawToFriendly(randombytes(31)),
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfFullVerkeySizeIs33Bytes(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    parameters = {
        'dest': rawToFriendly(randombytes(16)),
        'verkey': rawToFriendly(randombytes(33)),
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfAbbrevVerkeySizeIs15Bytes(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    parameters = {
        'dest': rawToFriendly(randombytes(16)),
        'verkey': '~' + rawToFriendly(randombytes(15)),
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1108')
def testSendNymFailsIfAbbrevVerkeySizeIs17Bytes(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    parameters = {
        'dest': rawToFriendly(randombytes(16)),
        'verkey': '~' + rawToFriendly(randombytes(17)),
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfUuidIdentifierIsHexEncoded(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    parameters = {
        'dest': friendlyToHexStr(createUuidIdentifier()),
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfFullVerkeyIsHexEncoded(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()
    parameters = {
        'dest': uuidIdentifier,
        'verkey': friendlyToHexStr(fullVerkey),
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfAbbrevVerkeyIsHexEncoded(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': '~' + friendlyToHexStr(abbrevVerkey.replace('~', '')),
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfIdentifierContainsNonBase58Characters(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    uuidIdentifier = createUuidIdentifier()
    parameters = {
        'dest': uuidIdentifier[:5] + '/' + uuidIdentifier[6:],
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfFullVerkeyContainsNonBase58Characters(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()
    parameters = {
        'dest': uuidIdentifier,
        'verkey': fullVerkey[:5] + '/' + fullVerkey[6:],
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfAbbrevVerkeyContainsNonBase58Characters(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey[:6] + '/' + abbrevVerkey[7:],
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfFullVerkeyContainsTilde(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()
    parameters = {
        'dest': uuidIdentifier,
        'verkey': '~' + fullVerkey,
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1109')
def testSendNymFailsIfAbbrevVerkeysdk_pool_handleesNotContainTilde(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey.replace('~', ''),
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1110')
def testSendNymFailsIfRoleIsUnknown(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': 'SUPERVISOR'
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1110')
def testSendNymFailsIfRoleIsSpecifiedUsingNumericCode(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': ENDORSER.value
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1111')
def testSendNymHasInvalidSyntaxIfParametersOrderIsWrong(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    halfKeyIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    parameters = {
        'dest': halfKeyIdentifier,
        'verkey': abbrevVerkey,
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1111')
def testSendNymHasInvalidSyntaxIfIdentifierIsEmpty(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    _, fullVerkey = createUuidIdentifierAndFullVerkey()
    parameters = {
        'dest': '',
        'verkey': fullVerkey,
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1111')
def testSendNymHasInvalidSyntaxIfIdentifierIsOmitted(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    _, fullVerkey = createUuidIdentifierAndFullVerkey()
    parameters = {
        'verkey': fullVerkey,
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


def testSendNymHasInvalidSyntaxForUuidIdentifierAndEmptyVerkey(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    parameters = {
        'dest': createUuidIdentifier(),
        'verkey': '',
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'Neither a full verkey nor an abbreviated one')


@pytest.mark.skip(reason='SOV-1111')
def testSendNymHasInvalidSyntaxIfIdentifierAndVerkeyAreOmitted(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    parameters = {
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1111')
def testSendNymHasInvalidSyntaxIfUnknownParameterIsPassed(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    uuidIdentifier, fullVerkey = createUuidIdentifierAndFullVerkey()
    parameters = {
        'dest': uuidIdentifier,
        'verkey': fullVerkey,
        'role': ENDORSER,
        'extra': 42
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


def testSendNymHasInvalidSyntaxIfAllParametersAreOmitted(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    for f in nym_request[OPERATION].keys():
        nym_request[OPERATION][f] = ''

    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'Reason: client request invalid')
