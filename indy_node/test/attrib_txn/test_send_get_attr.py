import pytest
import json

from indy.ledger import build_get_attrib_request
from libnacl.secret import SecretBox
from hashlib import sha256

from plenum.common.exceptions import RequestNackedException

from plenum.test.helper import sdk_get_and_check_replies

from indy_node.test.helper import createUuidIdentifier, sdk_add_attribute_and_check, \
    sdk_get_attribute_and_check, modify_field
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request

attrib_name = 'dateOfBirth'

secretBox = SecretBox()
enc_data = secretBox.encrypt(json.dumps({'name': 'Alice'}).encode()).hex()
hash_data = sha256(json.dumps({'name': 'Alice'}).encode()).hexdigest()


@pytest.fixture(scope="module")
def send_raw_attrib(looper, sdk_pool_handle, sdk_wallet_trustee):
    rep = sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_trustee,
                                      json.dumps({
                                          attrib_name: {
                                              'dayOfMonth': 23,
                                              'year': 1984,
                                              'month': 5
                                          }
                                      }))

    return rep


@pytest.fixture(scope="module")
def send_enc_attrib(looper, sdk_pool_handle, sdk_wallet_trustee):
    rep = sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_trustee, None,
                                      enc=json.dumps({attrib_name: enc_data}))
    return rep


@pytest.fixture(scope="module")
def send_hash_attrib(looper, sdk_pool_handle, sdk_wallet_trustee):
    rep = sdk_add_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_trustee, None,
                                      xhash=hash_data)
    return rep


@pytest.mark.attrib_txn
def test_send_get_attr_succeeds_for_existing_uuid_dest(
        looper, sdk_pool_handle, sdk_wallet_trustee, send_raw_attrib):
    wh, did = sdk_wallet_trustee
    sdk_get_attribute_and_check(looper, sdk_pool_handle, sdk_wallet_trustee, did, attrib_name)


@pytest.mark.attrib_txn
def test_send_get_attr_fails_for_nonexistent_uuid_dest(
        looper, sdk_pool_handle, sdk_wallet_trustee, send_raw_attrib):
    _, submitter_did = sdk_wallet_trustee
    req = looper.loop.run_until_complete(
        build_get_attrib_request(submitter_did, submitter_did, attrib_name, None, None))
    req = modify_field(req, submitter_did[:-10], 'operation', 'dest')
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, req)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [request_couple])
    e.match('should be one of \[16, 32\]')


@pytest.mark.attrib_txn
def test_send_get_attr_fails_for_invalid_attrib(
        looper, sdk_pool_handle, sdk_wallet_trustee, send_raw_attrib):
    did = createUuidIdentifier()
    _, submitter_did = sdk_wallet_trustee
    req = looper.loop.run_until_complete(
        build_get_attrib_request(submitter_did, did, attrib_name, None, None))
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, req)
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.attrib_txn
def test_send_get_attr_fails_with_missing_dest(
        looper, sdk_pool_handle, sdk_wallet_trustee, send_raw_attrib):
    _, submitter_did = sdk_wallet_trustee
    req = looper.loop.run_until_complete(
        build_get_attrib_request(submitter_did, submitter_did, attrib_name, None, None))
    req = modify_field(req, '', 'operation', 'dest')
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, req)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [request_couple])
    e.match('should be one of \[16, 32\]')


@pytest.mark.attrib_txn
def test_send_get_attr_fails_with_missing_attrib(
        looper, sdk_pool_handle, sdk_wallet_trustee, send_raw_attrib):
    _, submitter_did = sdk_wallet_trustee
    req = looper.loop.run_until_complete(
        build_get_attrib_request(submitter_did, submitter_did, attrib_name, None, None))
    req = json.loads(req)
    del req['operation']['raw']
    req = json.dumps(req)
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, req)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [request_couple])
    e.match('missed fields')


@pytest.mark.attrib_txn
def test_send_get_attr_enc_succeeds_for_existing_uuid_dest(
        looper, sdk_pool_handle, sdk_wallet_trustee, send_enc_attrib):
    _, submitter_did = sdk_wallet_trustee
    req = looper.loop.run_until_complete(
        build_get_attrib_request(submitter_did, submitter_did, None, None, attrib_name))
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, req)
    sdk_get_and_check_replies(looper, [request_couple])


@pytest.mark.attrib_txn
def test_send_get_attr_hash_succeeds_for_existing_uuid_dest(
        looper, sdk_pool_handle, sdk_wallet_trustee, send_hash_attrib):
    _, submitter_did = sdk_wallet_trustee
    req = looper.loop.run_until_complete(
        build_get_attrib_request(submitter_did, submitter_did, None, hash_data, None))
    request_couple = sdk_sign_and_send_prepared_request(looper, sdk_wallet_trustee,
                                                        sdk_pool_handle, req)
    sdk_get_and_check_replies(looper, [request_couple])
