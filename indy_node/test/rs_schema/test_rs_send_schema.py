import uuid
import json

import pytest
from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.types import SetRsSchemaDataField
from indy_node.test.api.helper import sdk_write_rs_schema_and_check, build_rs_schema_request
from plenum.common.exceptions import RequestRejectedException


def test_send_rs_schema_multiple_attrib(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
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
    reqId = uuid.uuid1().fields[0]
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
        "reqId": reqId,
        "protocolVersion": 2
    }
    request_json = json.dumps(txn_dict)

    with pytest.raises(Exception) as ex_info:
        sdk_write_rs_schema_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)
    ex_info.match(
        "validation error"
    )


def test_can_not_send_rs_schema_invalid_meta_type(looper, sdk_pool_handle, sdk_wallet_endorser):
    _, identifier = sdk_wallet_endorser
    authors_did, name, version, type = identifier, "ISO18023_Drivers_License", "1.3", "8"
    _id = identifier + ':' + type + ':' + name + ':' + version
    schema = {'@id': _id}
    reqId = uuid.uuid1().fields[0]
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
        "reqId": reqId,
        "protocolVersion": 2
    }
    request_json = json.dumps(txn_dict)

    with pytest.raises(Exception) as ex_info:
        sdk_write_rs_schema_and_check(looper, sdk_pool_handle, sdk_wallet_endorser, request_json)
    ex_info.match(
        "validation error"
    )


def test_rs_schema_over_maximum_attrib():
    attribs = []
    for i in range(131072 + 1):
        attribs.append('attrib' + str(i))

    schema = SetRsSchemaDataField()
    with pytest.raises(Exception) as ex_info:
        schema.validate({
            "schema": attribs})
    ex_info.match(
        "validation error"
    )
