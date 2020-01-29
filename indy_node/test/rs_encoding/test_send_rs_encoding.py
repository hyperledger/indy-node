import uuid
import json

import pytest
from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.types import SetRsEncodingDataField
from indy_node.test.api.helper import sdk_write_request_and_check, build_rs_encoding_request
from plenum.common.exceptions import RequestRejectedException


def test_send_rs_encoding(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "indy_encoding_sha", "1.1", "9"
    _id = identifier + ':' + type + ':' + name + ':' + version
    encoding = "UTF-8_SHA-256-2"
    request_json = build_rs_encoding_request(identifier, encoding, name, version)
    sdk_write_request_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)


def test_can_not_send_same_rs_encoding(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "indy_encoding_sha", "1.1", "9"
    _id = identifier + ':' + type + ':' + name + ':' + version
    encoding = "UTF-8_SHA-256-2"
    request_json = build_rs_encoding_request(identifier, encoding, name, version)
    sdk_write_request_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)

    with pytest.raises(RequestRejectedException,
                       match=str(AuthConstraintForbidden())):
        request_json = build_rs_encoding_request(identifier, encoding, name, version)
        sdk_write_request_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)


def test_can_not_send_rs_encoding_missing_meta_type(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "indy_encoding_sha", "1.3", "9"
    _id = identifier + ':' + type + ':' + name + ':' + version
    encoding = "UTF-8_SHA-256-2"
    reqId = uuid.uuid1().fields[0]
    txn_dict = {
        'operation': {
            'type': "202",
            'meta': {
                #'type': "encode",
                'name': name,
                'version': version
            },
            'data': {
                'encoding': encoding
            }
        },
        "identifier": identifier,
        "reqId": reqId,
        "protocolVersion": 2
    }
    request_json = json.dumps(txn_dict)

    with pytest.raises(Exception) as ex_info:
        sdk_write_request_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)
    ex_info.match(
        "validation error"
    )


def test_can_not_send_rs_encoding_invalid_meta_type(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "indy_encoding_sha", "1.3", "9"
    _id = identifier + ':' + type + ':' + name + ':' + version
    encoding = "UTF-8_SHA-256-2"
    reqId = uuid.uuid1().fields[0]
    txn_dict = {
        'operation': {
            'type': "202",
            'meta': {
                'type': "Allen",
                'name': name,
                'version': version
            },
            'data': {
                'encoding': encoding
            }
        },
        "identifier": identifier,
        "reqId": reqId,
        "protocolVersion": 2
    }
    request_json = json.dumps(txn_dict)

    with pytest.raises(Exception) as ex_info:
        sdk_write_request_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)
    ex_info.match(
        "validation error"
    )


def test_rs_encoding_over_maximum_str():
    attribs = []
    for i in range(131072 + 1):
        attribs.append('attrib' + str(i))

    encoding = SetRsEncodingDataField()
    with pytest.raises(Exception) as ex_info:
        encoding.validate({
            "encoding": ''.join(attribs)
        })
    ex_info.match(
        "validation error"
    )
