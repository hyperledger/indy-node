import json

import pytest
from indy.ledger import build_get_schema_request
from plenum.common.exceptions import RequestNackedException

from plenum.common.constants import DATA, NAME, VERSION, TXN_METADATA, TXN_METADATA_SEQ_NO

from plenum.common.types import OPERATION

from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_and_check_replies

from indy_node.test.api.helper import sdk_write_schema
from indy_node.test.helper import createUuidIdentifier, modify_field


@pytest.fixture(scope="module")
def send_schema(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee):
    schema_json, _ = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trustee)
    return json.loads(schema_json)['id']


@pytest.fixture(scope="module")
def send_schema_seq_no(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee):
    _, reply = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trustee)
    return reply['result'][TXN_METADATA][TXN_METADATA_SEQ_NO]


def test_send_get_schema_succeeds(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_schema):
    _, did = sdk_wallet_trustee

    request = looper.loop.run_until_complete(build_get_schema_request(did, send_schema))
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo']


def test_send_get_schema_as_client(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_client, send_schema):
    _, did = sdk_wallet_client

    request = looper.loop.run_until_complete(build_get_schema_request(did, send_schema))
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_client, request)])
    assert rep[0][1]['result']['seqNo']


def test_send_get_schema_fails_with_invalid_name(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_schema):
    _, did = sdk_wallet_trustee

    request = looper.loop.run_until_complete(build_get_schema_request(did, send_schema))
    request = modify_field(request, 'name111', OPERATION, DATA, NAME)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo'] is None


def test_send_get_schema_fails_with_invalid_dest(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_schema):
    uuid_identifier = createUuidIdentifier()
    _, did = sdk_wallet_trustee

    request = looper.loop.run_until_complete(build_get_schema_request(did, send_schema))
    request = modify_field(request, uuid_identifier, OPERATION, 'dest')
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo'] is None


def test_send_get_schema_fails_with_invalid_version(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_schema):
    _, did = sdk_wallet_trustee

    request = looper.loop.run_until_complete(build_get_schema_request(did, send_schema))
    request = modify_field(request, '2.0', OPERATION, DATA, VERSION)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo'] is None


def test_send_get_schema_fails_with_invalid_version_syntax(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_schema):
    _, did = sdk_wallet_trustee

    request = looper.loop.run_until_complete(build_get_schema_request(did, send_schema))
    request = modify_field(request, 'asd', OPERATION, DATA, VERSION)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('version consists of 1 components, but it should contain \(2, 3\)')


def test_send_get_schema_fails_without_version(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_schema):
    _, did = sdk_wallet_trustee

    request = looper.loop.run_until_complete(build_get_schema_request(did, send_schema))
    request = json.loads(request)
    del request[OPERATION][DATA][VERSION]
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - version')


def test_send_get_schema_fails_without_name(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_schema):
    _, did = sdk_wallet_trustee

    request = looper.loop.run_until_complete(build_get_schema_request(did, send_schema))
    request = json.loads(request)
    del request[OPERATION][DATA][NAME]
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - name')


def test_send_get_schema_fails_without_dest(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_schema):
    _, did = sdk_wallet_trustee

    request = looper.loop.run_until_complete(build_get_schema_request(did, send_schema))
    request = json.loads(request)
    del request[OPERATION]['dest']
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - dest')
