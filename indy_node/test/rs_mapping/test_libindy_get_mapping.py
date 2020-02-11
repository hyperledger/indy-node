import json

import pytest

from indy_node.test.rs_mapping.templates import TEST_1
from plenum.common.exceptions import RequestNackedException

from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_and_check_replies

from indy_node.test.api.helper import build_rs_mapping_request, \
    build_get_rs_mapping_request as build_request, submit_n_check_req
from indy_node.test.helper import createUuidIdentifier


@pytest.fixture(scope="module")
def sent_results(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee):
    _, identifier = sdk_wallet_trustee
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License_Mapping", "1.1", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    mapping = TEST_1
    request_json = build_rs_mapping_request(identifier, mapping, name, version)
    result = submit_n_check_req(looper, sdk_pool_handle, sdk_wallet_trustee, request_json)
    return result


@pytest.fixture(scope="module")
def txnId(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, sent_results):
    return sent_results['result']['txnMetadata']['txnId']


@pytest.fixture(scope="module")
def seqNo(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee,):
    return sent_results['result']['txnMetadata']['seqNo']


def test_get_mapping(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, txnId):
    _, did = sdk_wallet_trustee
    request = build_request(did, txnId)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo']


def test_get_mapping_as_client(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_client, txnId):
    _, did = sdk_wallet_client
    request = build_request(did, txnId)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_client, request)])
    assert rep[0][1]['result']['seqNo']


def test_get_mapping_invalid_name(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, txnId):
    _, did = sdk_wallet_trustee
    identifier, type, name, version = txnId.split(':')
    _id = identifier + ':' + type + ':' + "invalid_name" + ':' + version
    request = build_request(did, _id)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo'] is None


def test_get_mapping_invalid_from(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, txnId):
    uuid_identifier = createUuidIdentifier()
    _, did = sdk_wallet_trustee
    identifier, type, name, version = txnId.split(':')
    _id = uuid_identifier + ':' + type + ':' + name + ':' + version
    request = build_request(did, _id)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo'] is None


def test_get_mapping_invalid_version(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, txnId):
    _, did = sdk_wallet_trustee
    identifier, type, name, version = txnId.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + "2.0"
    request = build_request(did, _id)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo'] is None


def test_get_mapping_invalid_version_syntax(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, txnId):
    _, did = sdk_wallet_trustee

    identifier, type, name, version = txnId.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + "asd"
    request = build_request(did, _id)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match("Invalid version: 'asd'")


def test_get_mapping_empty_version(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, txnId):
    _, did = sdk_wallet_trustee

    identifier, type, name, version = txnId.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + version
    request = build_request(did, _id)
    request = json.loads(request)
    del request['operation']['meta']['version']
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - version')


def test_get_mapping_empty_name(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, txnId):
    _, did = sdk_wallet_trustee
    identifier, type, name, version = txnId.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + version
    request = build_request(did, _id)
    request = json.loads(request)
    del request['operation']['meta']['name']
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - name')


def test_get_mapping_empty_from(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, txnId):
    _, did = sdk_wallet_trustee
    identifier, type, name, version = txnId.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + version
    request = build_request(did, _id)
    request = json.loads(request)
    del request['operation']['from']
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - from')


def test_get_mapping_empty_meta_data_type(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, txnId):
    _, did = sdk_wallet_trustee
    identifier, type, name, version = txnId.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + version
    request = build_request(did, _id)
    request = json.loads(request)
    del request['operation']['meta']['type']
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - type')
