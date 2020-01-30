import json

import pytest
from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.types import SetRsSchemaDataField
from indy_node.test.api.helper import sdk_write_rs_schema_and_check, build_rs_schema_request
from indy_node.test.rs_schema.templates import TEST_1
from plenum.common.exceptions import RequestRejectedException
from indy_node.test.api.helper import req_id
_reqId = req_id()


def test_send_rs_schema_multiple_attrib(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.1", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = TEST_1
    schema['@id'] = _id
    request_json = build_rs_schema_request(identifier, schema, name, version)
    sdk_write_rs_schema_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)


def test_send_rs_schema_one_attrib(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.2", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = {'@id': _id,
              '@type': "0od"}
    request_json = build_rs_schema_request(identifier, schema, name, version)
    sdk_write_rs_schema_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)


def test_can_not_send_same_rs_schema(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.3", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = {'@id': _id,
              '@type': "0od"}
    request_json = build_rs_schema_request(identifier, schema, name, version)
    sdk_write_rs_schema_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)

    with pytest.raises(RequestRejectedException,
                       match=str(AuthConstraintForbidden())):
        request_json = build_rs_schema_request(identifier, schema, name, version)
        sdk_write_rs_schema_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)


def test_can_not_send_rs_schema_missing_id(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.3", "8"
    # _id = identifier + ':' + type + ':' + name + ':' + version
    schema = {'@type': "0od"}
    request_json = build_rs_schema_request(identifier, schema, name, version)

    with pytest.raises(Exception) as ex_info:
        sdk_write_rs_schema_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)
    ex_info.match(
        "validation error"
    )


def test_can_not_send_rs_schema_missing_type(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.3", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = {'@id': _id}
    request_json = build_rs_schema_request(identifier, schema, name, version)

    with pytest.raises(Exception) as ex_info:
        sdk_write_rs_schema_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)
    ex_info.match(
        "validation error"
    )


def test_can_not_send_rs_schema_missing_meta_type(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.3", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = {'@id': _id}
    txn_dict = {
        'operation': {
            'type': "201",
            'meta': {
                #'type': "sch",
                'name': name,
                'version': version
            },
            'data': {
                'schema': schema
            }
        },
        "identifier": identifier,
        "reqId": next(_reqId),
        "protocolVersion": 2
    }
    request_json = json.dumps(txn_dict)

    with pytest.raises(Exception) as ex_info:
        sdk_write_rs_schema_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)
    ex_info.match("validation error")


def test_can_not_send_rs_schema_invalid_meta_type(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.3", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = {'@id': _id}
    txn_dict = {
        'operation': {
            'type': "201",
            'meta': {
                'type': "Allen",
                'name': name,
                'version': version
            },
            'data': {
                'schema': schema
            }
        },
        "identifier": identifier,
        "reqId": next(_reqId),
        "protocolVersion": 2
    }
    request_json = json.dumps(txn_dict)

    with pytest.raises(Exception) as ex_info:
        sdk_write_rs_schema_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)
    ex_info.match(
        "validation error"
    )


def test_rs_schema_over_maximum_size():
    attribs = {}
    for i in range(131072 + 1):
        attribs['attrib' + str(i)] = str(i)
    schema = SetRsSchemaDataField()
    with pytest.raises(Exception) as ex_info:
        schema.validate({
            "schema": attribs})
    ex_info.match('length of rs_schema is {}; should be <= {}'.format(131073, 131072))


def test_rs_schema_empty_failure():
    schema = SetRsSchemaDataField()
    with pytest.raises(Exception) as ex_info:
        schema.validate({
            "schema": {}})
    ex_info.match('validation error')
