import json

import pytest
from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.types import SetRsMappingDataField
from indy_node.test.api.helper import submit_n_check_req as send_request, build_rs_mapping_request as build_request
from indy_node.test.rs_mapping.templates import TEST_1
from plenum.common.exceptions import RequestRejectedException
from indy_node.test.api.helper import req_id
_reqId = req_id()


def test_mapping_multiple_attrib(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.1", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = TEST_1
    schema['@id'] = _id
    request_json = build_request(identifier, schema, name, version)
    send_request(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)


def test_mapping_one_attrib(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.2", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = {'@id': _id,
              '@type': "0od"}
    request_json = build_request(identifier, schema, name, version)
    send_request(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)


def test__same_rs_mapping(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.3", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = {'@id': _id,
              '@type': "0od"}
    request_json = build_request(identifier, schema, name, version)
    send_request(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)

    with pytest.raises(RequestRejectedException,
                       match=str(AuthConstraintForbidden())):
        request_json = build_request(identifier, schema, name, version)
        send_request(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)


def test_mapping_missing_id(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.3", "8"
    # _id = identifier + ':' + type + ':' + name + ':' + version
    schema = {'@type': "0od"}
    request_json = build_request(identifier, schema, name, version)

    with pytest.raises(Exception) as ex_info:
        send_request(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)
    ex_info.match(
        "validation error"
    )


def test_mapping_missing_type(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.3", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = {'@id': _id}
    request_json = build_request(identifier, schema, name, version)

    with pytest.raises(Exception) as ex_info:
        send_request(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)
    ex_info.match(
        "validation error"
    )


def test_mapping_missing_meta_type(looper, sdk_pool_handle, sdk_wallet_endorser):
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
        send_request(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)
    ex_info.match("validation error")


def test_mapping_invalid_meta_type(looper, sdk_pool_handle, sdk_wallet_endorser):
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
        send_request(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)
    ex_info.match(
        "validation error"
    )


def test_mapping_over_maximum_size():
    attribs = {}
    for i in range(131072 + 1):
        attribs['attrib' + str(i)] = str(i)
    validator = SetRsMappingDataField()
    with pytest.raises(Exception) as ex_info:
        validator.validate({
            "mapping": attribs})
    ex_info.match('length of rs_mapping is {}; should be <= {}'.format(131073, 131072))


def test_mapping_empty_failure():
    validator = SetRsMappingDataField()
    with pytest.raises(Exception) as ex_info:
        validator.validate({
            "mapping": {}})
    ex_info.match('validation error')
