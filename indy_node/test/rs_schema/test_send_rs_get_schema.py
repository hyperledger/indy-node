import json

import pytest

from indy_node.test.rs_schema.templates import TEST_1
from plenum.common.exceptions import RequestNackedException

from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_and_check_replies

from indy_node.test.api.helper import sdk_write_rs_schema, build_rs_schema_request, \
    build_get_rs_schema_request
from indy_node.test.helper import createUuidIdentifier


@pytest.fixture(scope="module")
def send_rs_schema(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee):
    _, identifier = sdk_wallet_trustee
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.1", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = {
            '@id': _id,
            '@context': "ctx:sov:2f9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
            '@type': "rdfs:Class",
            "rdfs:comment": "ISO18013 International Driver License",
            "rdfs:label": "Driver License",
            "rdfs:subClassOf": {
                "@id": "sch:Thing"
            },
            "driver": "Driver",
            "dateOfIssue": "Date",
            "dateOfExpiry": "Date",
            "issuingAuthority": "Text",
            "licenseNumber": "Text",
            "categoriesOfVehicles": {
                "vehicleType": "Text",
                "vehicleType-input": {
                    "@type": "sch:PropertyValueSpecification",
                    "valuePattern": "^(A|B|C|D|BE|CE|DE|AM|A1|A2|B1|C1|D1|C1E|D1E)$"
                },
                "dateOfIssue": "Date",
                "dateOfExpiry": "Date",
                "restrictions": "Text",
                "restrictions-input": {
                    "@type": "sch:PropertyValueSpecification",
                    "valuePattern": "^([A-Z]|[1-9])$"
                }
            },
            "administrativeNumber": "Text"
        }
    request_json = build_rs_schema_request(identifier, schema, name, version)
    reply = sdk_write_rs_schema(looper, sdk_pool_handle, sdk_wallet_trustee, request_json)
    return reply['result']['txnMetadata']['txnId']


@pytest.fixture(scope="module")
def send_rs_schema_seq_no(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee):
    _, identifier = sdk_wallet_trustee
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.1", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = TEST_1
    schema['@id'] = _id
    request_json = build_rs_schema_request(identifier, schema, name, version)
    schema_json, reply = sdk_write_rs_schema(looper, sdk_pool_handle, sdk_wallet_trustee, request_json)
    return reply['result']['txnMetadata']['seqNo']


@pytest.fixture(scope="module")
def send_rs_schema_req(looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee):
    _, identifier = sdk_wallet_trustee
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.1", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = TEST_1
    schema['@id'] = _id
    request_json = build_rs_schema_request(identifier, schema, name, version)
    schema_json, reply = sdk_write_rs_schema(looper, sdk_pool_handle, sdk_wallet_trustee, request_json)
    return schema_json, reply


def test_send_get_rs_schema_succeeds(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_schema):
    _, did = sdk_wallet_trustee
    schema_txnId = send_rs_schema
    request = build_get_rs_schema_request(did, schema_txnId)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo']


def test_send_get_rs_schema_as_client(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_client, send_rs_schema):
    _, did = sdk_wallet_client

    schema_txnId = send_rs_schema
    request = build_get_rs_schema_request(did, schema_txnId)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_client, request)])
    assert rep[0][1]['result']['seqNo']


def test_send_get_rs_schema_fails_with_invalid_name(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_schema):
    _, did = sdk_wallet_trustee

    identifier, type, name, version = send_rs_schema.split(':')
    _id = identifier + ':' + type + ':' + "invalid_name" + ':' + version
    request = build_get_rs_schema_request(did, _id)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo'] is None


def test_send_get_rs_schema_fails_with_invalid_from(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_schema):
    uuid_identifier = createUuidIdentifier()
    _, did = sdk_wallet_trustee

    identifier, type, name, version = send_rs_schema.split(':')
    _id = uuid_identifier + ':' + type + ':' + name + ':' + version
    request = build_get_rs_schema_request(did, _id)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo'] is None


def test_send_get_rs_schema_fails_with_invalid_version(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_schema):
    _, did = sdk_wallet_trustee

    identifier, type, name, version = send_rs_schema.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + "2.0"
    request = build_get_rs_schema_request(did, _id)
    rep = sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    assert rep[0][1]['result']['seqNo'] is None


def test_send_get_rs_schema_fails_with_invalid_version_syntax(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_schema):
    _, did = sdk_wallet_trustee

    identifier, type, name, version = send_rs_schema.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + "asd"
    request = build_get_rs_schema_request(did, _id)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match("Invalid version: 'asd'")


def test_send_get_rs_schema_fails_without_version(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_schema):
    _, did = sdk_wallet_trustee

    identifier, type, name, version = send_rs_schema.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + version
    request = build_get_rs_schema_request(did, _id)
    request = json.loads(request)
    del request['operation']['meta']['version']
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - version')


def test_send_get_rs_schema_fails_without_name(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_schema):
    _, did = sdk_wallet_trustee

    identifier, type, name, version = send_rs_schema.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + version
    request = build_get_rs_schema_request(did, _id)
    request = json.loads(request)
    del request['operation']['meta']['name']
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - name')


def test_send_get_rs_schema_fails_without_from(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_schema):
    _, did = sdk_wallet_trustee

    identifier, type, name, version = send_rs_schema.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + version
    request = build_get_rs_schema_request(did, _id)
    request = json.loads(request)
    del request['operation']['from']
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - from')


def test_get_rs_schema_fails_without_meta_data_type(
        looper, sdk_pool_handle, nodeSet, sdk_wallet_trustee, send_rs_schema):
    _, did = sdk_wallet_trustee

    identifier, type, name, version = send_rs_schema.split(':')
    _id = identifier + ':' + type + ':' + name + ':' + version
    request = build_get_rs_schema_request(did, _id)
    request = json.loads(request)
    del request['operation']['meta']['type']
    request = json.dumps(request)
    with pytest.raises(RequestNackedException) as e:
        sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request)])
    e.match('missed fields - type')