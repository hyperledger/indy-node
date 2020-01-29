import json

import pytest
from plenum.common.exceptions import RequestNackedException

from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_and_check_replies

from indy_node.test.api.helper import sdk_write_request, build_rs_encoding_request, \
    build_get_rs_encoding_request
from indy_node.test.helper import createUuidIdentifier


@pytest.fixture(scope="module")
def send_rs_encoding(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee):
    _, identifier = sdk_wallet_trustee
    authors_did, name, version, type = identifier, "indy_encoding_sha", "1.3", "9"
    _id = identifier + ':' + type + ':' + name + ':' + version
    encoding = "UTF-8_SHA-256-2"
    request_json = build_rs_encoding_request(identifier, encoding, name, version)
    reply = sdk_write_request(looper, sdk_pool_handle, sdk_wallet_trustee, request_json)
    return reply['result']['txnMetadata']['txnId']


@pytest.fixture(scope="module")
def send_rs_encoding_seq_no(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee):
    _, identifier = sdk_wallet_trustee
    authors_did, name, version, type = identifier, "indy_encoding_sha", "1.3", "9"
    _id = identifier + ':' + type + ':' + name + ':' + version
    encoding = "UTF-8_SHA-256-2"
    request_json = build_rs_encoding_request(identifier, encoding, name, version)
    encoding_json, reply = sdk_write_request(looper, sdk_pool_handle, sdk_wallet_trustee, request_json)
    return reply['result']['txnMetadata']['seqNo']


@pytest.fixture(scope="module")
def send_rs_encoding_req(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee):
    _, identifier = sdk_wallet_trustee
    authors_did, name, version, type = identifier, "indy_encoding_sha", "1.3", "9"
    _id = identifier + ':' + type + ':' + name + ':' + version
    encoding = "UTF-8_SHA-256-2"
    request_json = build_rs_encoding_request(identifier, encoding, name, version)
    encoding_json, reply = sdk_write_request(looper, sdk_pool_handle, sdk_wallet_trustee, request_json)
    return encoding_json, reply


def test_send_get_rs_encoding_succeeds(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_encoding):
    _, did = sdk_wallet_trustee
    txnId = send_rs_encoding
    request = build_get_rs_encoding_request(did, txnId)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo']


def test_send_get_rs_encoding_as_client(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_client, send_rs_encoding):
    _, did = sdk_wallet_client
    txnId = send_rs_encoding
    request = build_get_rs_encoding_request(did, txnId)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_client, request)])
    assert rep[0][1]['result']['seqNo']


def test_send_get_rs_encoding_fails_with_invalid_name(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_encoding):
    _, did = sdk_wallet_trustee
    identifier, type, name, version = send_rs_encoding.split(':')
    _id = identifier + ':' + type + ':' + "invalid_name" + ':' + version
    request = build_get_rs_encoding_request(did, _id)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo'] is None


def test_send_get_rs_encoding_fails_with_invalid_from(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_encoding):
    uuid_identifier = createUuidIdentifier()
    _, did = sdk_wallet_trustee
    identifier, type, name, version = send_rs_encoding.split(':')
    _id = uuid_identifier + ':' + type + ':' + name + ':' + version
    request = build_get_rs_encoding_request(did, _id)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo'] is None


def test_send_get_rs_encoding_fails_with_invalid_version(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_encoding):
    _, did = sdk_wallet_trustee
    identifier, type, name, version = send_rs_encoding.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + "2.0"
    request = build_get_rs_encoding_request(did, _id)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo'] is None


def test_send_get_rs_encoding_fails_with_invalid_version_syntax(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_encoding):
    _, did = sdk_wallet_trustee
    identifier, type, name, version = send_rs_encoding.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + "asd"
    request = build_get_rs_encoding_request(did, _id)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match("Invalid version: 'asd'")


def test_send_get_rs_encoding_fails_without_version(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_encoding):
    _, did = sdk_wallet_trustee
    identifier, type, name, version = send_rs_encoding.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + version
    request = build_get_rs_encoding_request(did, _id)
    request = json.loads(request)
    del request['operation']['meta']['version']
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - version')


def test_send_get_rs_encoding_fails_without_name(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_encoding):
    _, did = sdk_wallet_trustee
    identifier, type, name, version = send_rs_encoding.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + version
    request = build_get_rs_encoding_request(did, _id)
    request = json.loads(request)
    del request['operation']['meta']['name']
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - name')


def test_send_get_rs_encoding_fails_without_from(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_encoding):
    _, did = sdk_wallet_trustee
    identifier, type, name, version = send_rs_encoding.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + version
    request = build_get_rs_encoding_request(did, _id)
    request = json.loads(request)
    del request['operation']['from']
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - from')


def test_get_rs_encoding_fails_without_meta_data_type(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_encoding):
    _, did = sdk_wallet_trustee
    identifier, type, name, version = send_rs_encoding.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + version
    request = build_get_rs_encoding_request(did, _id)
    request = json.loads(request)
    del request['operation']['meta']['type']
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - type')