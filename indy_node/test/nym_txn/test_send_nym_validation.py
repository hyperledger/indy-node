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


@pytest.mark.nym_txn
def test_send_nym_succeeds_for_uuid_identifier_ansdk_pool_handlemitted_verkey(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    parameters = {
        'dest': createUuidIdentifier(),
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.nym_txn
def test_send_nym_succeeds_for_uuid_identifier_and_full_verkey(
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


@pytest.mark.nym_txn
def test_send_nym_succeeds_for_half_key_identifier_and_abbrev_verkey(
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
def test_send_nym_fails_for_cryptonym_identifier_ansdk_pool_handlemitted_verkey(
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
def test_send_nym_fails_for_cryptonym_identifier_and_full_verkey(
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


@pytest.mark.nym_txn
def test_send_nym_fails_for_cryptonym_identifier_and_matched_abbrev_verkey(
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
def test_send_nym_fails_if_identifier_size_is15_bytes(
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
def test_send_nym_fails_if_identifier_size_is17_bytes(
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
def test_send_nym_fails_if_full_verkey_size_is31_bytes(
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
def test_send_nym_fails_if_full_verkey_size_is33_bytes(
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
def test_send_nym_fails_if_abbrev_verkey_size_is15_bytes(
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
def test_send_nym_fails_if_abbrev_verkey_size_is17_bytes(
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
def test_send_nym_fails_if_uuid_identifier_is_hex_encoded(
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
def test_send_nym_fails_if_full_verkey_is_hex_encoded(
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
def test_send_nym_fails_if_abbrev_verkey_is_hex_encoded(
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
def test_send_nym_fails_if_identifier_contains_non_base58_characters(
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
def test_send_nym_fails_if_full_verkey_contains_non_base58_characters(
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
def test_send_nym_fails_if_abbrev_verkey_contains_non_base58_characters(
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
def test_send_nym_fails_if_full_verkey_contains_tilde(
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
def test_send_nym_fails_if_abbrev_verkeysdk_pool_handlees_not_contain_tilde(
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
def test_send_nym_fails_if_role_is_unknown(
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
def test_send_nym_fails_if_role_is_specified_using_numeric_code(
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
def test_send_nym_has_invalid_syntax_if_parameters_order_is_wrong(
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
def test_send_nym_has_invalid_syntax_if_identifier_is_empty(
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
def test_send_nym_has_invalid_syntax_if_identifier_is_omitted(
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


@pytest.mark.nym_txn
def test_send_nym_has_invalid_syntax_for_uuid_identifier_and_empty_verkey(
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
def test_send_nym_has_invalid_syntax_if_identifier_and_verkey_are_omitted(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    parameters = {
        'role': ENDORSER
    }
    nym_request[OPERATION].update(parameters)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.skip(reason='SOV-1111')
def test_send_nym_has_invalid_syntax_if_unknown_parameter_is_passed(
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


@pytest.mark.nym_txn
def test_send_nym_has_invalid_syntax_if_all_parameters_are_omitted(
        looper, sdk_pool_handle, txnPoolNodeSet, nym_request, sdk_wallet_trustee):
    for f in nym_request[OPERATION].keys():
        nym_request[OPERATION][f] = ''

    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, json.dumps(nym_request))
    sdk_get_bad_response(looper, [request_couple], RequestNackedException,
                         'Reason: client request invalid')
