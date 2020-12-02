import copy
import json
from functools import reduce
from operator import getitem

import pytest

from indy_common.constants import RS_CONTENT, ENDORSER, RS_MAPPING_SCHEMA, RS_ID, \
    RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE, RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, RICH_SCHEMA, \
    RS_SCHEMA_TYPE_VALUE, RS_MAPPING_ENC, RS_MAPPING_RANK, RS_MAPPING_ATTRIBUTES
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_encoding_handler import \
    RichSchemaEncodingHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_handler import RichSchemaHandler
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rich_schema_mapping_handler import \
    RichSchemaMappingHandler
from indy_node.test.request_handlers.helper import add_to_idr
from indy_node.test.request_handlers.rich_schema.helper import make_rich_schema_object_exist, rs_req
from indy_node.test.rich_schema.templates import RICH_SCHEMA_ENCODING_EX1, RICH_SCHEMA_EX1
from plenum.common.constants import TRUSTEE
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.util import randomString

TEST_MAPPING = {
    '@id': "did:sov:8a9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
    '@context': "did:sov:2f9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
    '@type': "rdfs:Class",
    "schema": "did:sov:4e9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
    "attributes": {
        "attr1": [
            {
                "enc": "did:sov:1x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
                "rank": 3
            }
        ],
        "attr2": [
            {
                "enc": "did:sov:1x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
                "rank": 2
            },
            {
                "enc": "did:sov:2x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
                "rank": 1
            },
        ],
        "attr3": {
            "attr4": [
                {
                    "attr5": [
                        {
                            "enc": "did:sov:3x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
                            "rank": 4
                        }
                    ]
                },
                {
                    "attr6": [
                        {
                            "enc": "did:sov:3x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
                            "rank": 5
                        }
                    ]
                },
            ]
        },
        "issuer": [
            {
                "enc": "did:sov:1x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
                "rank": 7
            }
        ],
        "issuanceDate": [
            {
                "enc": "did:sov:1x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
                "rank": 6
            }
        ],
    }
}

TEST_ENCODING_1 = rs_req(RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE,
                         content=RICH_SCHEMA_ENCODING_EX1, id="did:sov:1x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD")

TEST_ENCODING_2 = rs_req(RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE,
                         content=RICH_SCHEMA_ENCODING_EX1, id="did:sov:2x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD")

TEST_ENCODING_3 = rs_req(RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE,
                         content=RICH_SCHEMA_ENCODING_EX1, id="did:sov:3x9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD")


@pytest.fixture()
def mapping_handler(db_manager, write_auth_req_validator):
    return RichSchemaMappingHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def rich_schema_handler(db_manager, write_auth_req_validator):
    return RichSchemaHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def encoding_handler(db_manager, write_auth_req_validator):
    return RichSchemaEncodingHandler(db_manager, write_auth_req_validator)


@pytest.fixture()
def rich_schema_req():
    id = "did:sov:4e9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD"
    content = copy.deepcopy(RICH_SCHEMA_EX1)
    content['@id'] = id
    return rs_req(RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE,
                  content=content, id=id)


@pytest.fixture()
def mapping_req(rich_schema_handler, encoding_handler, rich_schema_req):
    make_rich_schema_object_exist(rich_schema_handler, rich_schema_req)
    make_rich_schema_object_exist(encoding_handler, TEST_ENCODING_1)
    make_rich_schema_object_exist(encoding_handler, TEST_ENCODING_2)
    make_rich_schema_object_exist(encoding_handler, TEST_ENCODING_3)

    id = randomString()
    content = copy.deepcopy(TEST_MAPPING)
    content['@id'] = id
    req = rs_req(RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE,
                 content=content, id=id)

    add_to_idr(rich_schema_handler.database_manager.idr_cache, req.identifier, TRUSTEE)
    add_to_idr(rich_schema_handler.database_manager.idr_cache, req.endorser, ENDORSER)

    return req


def test_static_validation_pass(mapping_handler, mapping_req):
    mapping_handler.static_validation(mapping_req)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
@pytest.mark.parametrize('missing_field', ['schema', 'attributes'])
def test_static_validation_fail_no_schema_or_attribute(mapping_handler, mapping_req, status, missing_field):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop(missing_field, None)
    elif status == 'empty':
        content[missing_field] = ""
    elif status == 'none':
        content[missing_field] = None
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'{}' must be set in 'content'".format(missing_field)):
        mapping_handler.static_validation(mapping_req)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_fail_no_schema_and_attributes(mapping_handler, mapping_req, status):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    if status == 'missing':
        content.pop('attributes', None)
        content.pop('schema', None)
    elif status == 'empty':
        content['attributes'] = {}
        content['schema'] = {}
    elif status == 'none':
        content['attributes'] = None
        content['schema'] = None
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'schema' and 'attributes' must be set in 'content'"):
        mapping_handler.static_validation(mapping_req)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
@pytest.mark.parametrize('missing_field', ['issuer', 'issuanceDate'])
def test_static_validation_fail_no_issuer_or_issuance_date(mapping_handler, mapping_req, status, missing_field):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    if status == 'missing':
        content[RS_MAPPING_ATTRIBUTES].pop(missing_field, None)
    elif status == 'empty':
        content[RS_MAPPING_ATTRIBUTES][missing_field] = {}
    elif status == 'none':
        content[RS_MAPPING_ATTRIBUTES][missing_field] = None
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'{}' must be in content's 'attributes'".format(missing_field)):
        mapping_handler.static_validation(mapping_req)


@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
def test_static_validation_fail_no_issuance_date_and_issuer(mapping_handler, mapping_req, status):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    if status == 'missing':
        content[RS_MAPPING_ATTRIBUTES].pop('issuanceDate', None)
        content[RS_MAPPING_ATTRIBUTES].pop('issuer', None)
    elif status == 'empty':
        content[RS_MAPPING_ATTRIBUTES]['issuanceDate'] = {}
        content[RS_MAPPING_ATTRIBUTES]['issuer'] = {}
    elif status == 'none':
        content[RS_MAPPING_ATTRIBUTES]['issuanceDate'] = None
        content[RS_MAPPING_ATTRIBUTES]['issuer'] = None
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'issuer' and 'issuanceDate' must be in content's 'attributes'"):
        mapping_handler.static_validation(mapping_req)


def test_schema_dynamic_validation_passes(mapping_handler, mapping_req):
    mapping_handler.dynamic_validation(mapping_req, 0)


def test_dynamic_validation_not_existent_schema(mapping_handler, mapping_req):
    schema_id = randomString()
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    content[RS_MAPPING_SCHEMA] = schema_id
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match='Can not find a schema with id={}; please make sure that it has been added to the ledger'.format(
                           schema_id)):
        mapping_handler.dynamic_validation(mapping_req, 0)


def test_dynamic_validation_not_schema_in_schema_field(mapping_handler, mapping_req):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    content[RS_MAPPING_SCHEMA] = TEST_ENCODING_1.operation[RS_ID]
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'schema' field must reference a schema with rsType=sch"):
        mapping_handler.dynamic_validation(mapping_req, 0)


def get_mapping_attr_value(keys, mapping_content):
    return reduce(getitem, keys, mapping_content)


# a test against TEST_MAPPING
@pytest.mark.parametrize('enc_path, index', [
    (['attr1'], 0),
    (['attr2'], 0),
    (['attr2'], 1),
    (['attr3', 'attr4', 0, 'attr5'], 0),
    (['attr3', 'attr4', 1, 'attr6'], 0)
])
@pytest.mark.parametrize('status', ['missing', 'empty', 'none'])
@pytest.mark.parametrize('missing_field', [RS_MAPPING_ENC, RS_MAPPING_RANK])
def test_dynamic_validation_empty_field_in_encoding_desc(mapping_handler, mapping_req,
                                                         enc_path, index, status, missing_field):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    enc_dict = get_mapping_attr_value(enc_path, content[RS_MAPPING_ATTRIBUTES])[index]
    if status == 'missing':
        enc_dict.pop(missing_field, None)
    elif status == 'empty':
        enc_dict[missing_field] = ""
    elif status == 'none':
        enc_dict[missing_field] = None
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="{} must be set for the attribute '{}'".format(missing_field, enc_path[-1])):
        mapping_handler.dynamic_validation(mapping_req, 0)


# a test against TEST_MAPPING
@pytest.mark.parametrize('enc_path, index', [
    (['attr1'], 0),
    (['attr2'], 0),
    (['attr2'], 1),
    (['attr3', 'attr4', 0, 'attr5'], 0),
    (['attr3', 'attr4', 1, 'attr6'], 0)
])
@pytest.mark.parametrize('status', ['missing', 'empty', 'none', 'not_a_dict'])
def test_dynamic_validation_empty_encoding_desc(mapping_handler, mapping_req,
                                                enc_path, index, status):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    enc_list = get_mapping_attr_value(enc_path, content[RS_MAPPING_ATTRIBUTES])
    enc_dict = enc_list[index]
    if status == 'missing':
        enc_dict.pop(RS_MAPPING_ENC, None)
        enc_dict.pop(RS_MAPPING_RANK, None)
    elif status == 'empty':
        enc_dict[RS_MAPPING_ENC] = ""
        enc_dict[RS_MAPPING_RANK] = ""
    elif status == 'none':
        enc_dict[RS_MAPPING_ENC] = None
        enc_dict[RS_MAPPING_RANK] = None
    elif status == 'not_a_dict':
        enc_list[index] = "aaaa"
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="enc and rank must be set for the attribute '{}'".format(enc_path[-1])):
        mapping_handler.dynamic_validation(mapping_req, 0)


# a test against TEST_MAPPING
@pytest.mark.parametrize('enc_path, index', [
    (['attr1'], 0),
    (['attr2'], 0),
    (['attr2'], 1),
    (['attr3', 'attr4', 0, 'attr5'], 0),
    (['attr3', 'attr4', 1, 'attr6'], 0)
])
def test_dynamic_validation_not_existent_encoding(mapping_handler, mapping_req,
                                                  enc_path, index):
    wrong_id = randomString()
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    enc_dict = get_mapping_attr_value(enc_path, content[RS_MAPPING_ATTRIBUTES])[index]
    enc_dict[RS_MAPPING_ENC] = wrong_id
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="Can not find a referenced 'enc' with id={} in the '{}' attribute; please make sure that it has been added to the ledger".format(
                           wrong_id, enc_path[-1])):
        mapping_handler.dynamic_validation(mapping_req, 0)


# a test against TEST_MAPPING
@pytest.mark.parametrize('enc_path, index', [
    (['attr1'], 0),
    (['attr2'], 0),
    (['attr2'], 1),
    (['attr3', 'attr4', 0, 'attr5'], 0),
    (['attr3', 'attr4', 1, 'attr6'], 0)
])
def test_dynamic_validation_not_encoding_in_enc_field(mapping_handler, mapping_req,
                                                      rich_schema_req,
                                                      enc_path, index):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    enc_dict = get_mapping_attr_value(enc_path, content[RS_MAPPING_ATTRIBUTES])[index]
    enc_dict[RS_MAPPING_ENC] = rich_schema_req.operation[RS_ID]
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="'enc' field in the '{}' attribute must reference an encoding with rsType=enc".format(
                           enc_path[-1])):
        mapping_handler.dynamic_validation(mapping_req, 0)


# a test against TEST_MAPPING
@pytest.mark.parametrize('enc_path, index', [
    (['attr1'], 0),
    (['attr2'], 0),
    (['attr2'], 1),
    (['attr3', 'attr4', 0, 'attr5'], 0),
    (['attr3', 'attr4', 1, 'attr6'], 0),
    (['issuer'], 0),
    (['issuanceDate'], 0)
])
@pytest.mark.parametrize('rank_value', [0, 8, 9, 12, -1])
def test_dynamic_validation_rank_sequence(mapping_handler, mapping_req,
                                          rich_schema_req,
                                          enc_path, index, rank_value):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    enc_dict = get_mapping_attr_value(enc_path, content[RS_MAPPING_ATTRIBUTES])[index]
    enc_dict[RS_MAPPING_RANK] = rank_value
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="the attribute's ranks are not sequential: expected ranks are all values from 1 to 7"):
        mapping_handler.dynamic_validation(mapping_req, 0)


@pytest.mark.parametrize('enc_path, index', [
    (['attr1'], 0),
    (['attr2'], 0),
    (['attr2'], 1),
])
@pytest.mark.parametrize('rank_value', [4, 5, 6, 7])
def test_dynamic_validation_rank_same_rank(mapping_handler, mapping_req,
                                           rich_schema_req,
                                           enc_path, index, rank_value):
    content = copy.deepcopy(json.loads(mapping_req.operation[RS_CONTENT]))
    enc_dict = get_mapping_attr_value(enc_path, content[RS_MAPPING_ATTRIBUTES])[index]
    enc_dict[RS_MAPPING_RANK] = rank_value
    mapping_req.operation[RS_CONTENT] = json.dumps(content)

    with pytest.raises(InvalidClientRequest,
                       match="the attribute's ranks are not sequential: expected ranks are all values from 1 to 7"):
        mapping_handler.dynamic_validation(mapping_req, 0)
