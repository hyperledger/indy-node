import json

import pytest
from indy.ledger import parse_get_schema_response, build_get_schema_request

from indy_common.config import SCHEMA_ATTRIBUTES_LIMIT
from indy_node.test.api.helper import sdk_write_schema
from plenum.common.util import randomString
from plenum.config import NAME_FIELD_LIMIT
from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_reply


@pytest.fixture(scope="module")
def schema_json(looper, sdk_pool_handle, sdk_wallet_trustee):
    wallet_handle, identifier = sdk_wallet_trustee
    schema_json, _ = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trustee)
    schema_id = json.loads(schema_json)['id']

    request = looper.loop.run_until_complete(build_get_schema_request(identifier, schema_id))
    reply = sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request))[1]
    _, schema_json = looper.loop.run_until_complete(parse_get_schema_response(json.dumps(reply)))
    return schema_json


@pytest.fixture(scope="module")
def large_schema_json(looper, sdk_pool_handle, sdk_wallet_trustee):
    wallet_handle, identifier = sdk_wallet_trustee
    attrs = [randomString(size=NAME_FIELD_LIMIT) for _ in range(SCHEMA_ATTRIBUTES_LIMIT)]
    schema_json, _ = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trustee,
                                      multi_attribute=attrs, name="name_large", version="2.0")
    schema_id = json.loads(schema_json)['id']

    request = looper.loop.run_until_complete(build_get_schema_request(identifier, schema_id))
    reply = sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trustee, request))[1]
    _, schema_json = looper.loop.run_until_complete(parse_get_schema_response(json.dumps(reply)))
    return schema_json
