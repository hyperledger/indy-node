import json

from indy.anoncreds import issuer_create_schema
from indy.ledger import build_schema_request
from indy_client.test.cli.constants import SCHEMA_ADDED, SCHEMA_NOT_ADDED_DUPLICATE
from indy_node.test.api.helper import sdk_write_schema
from plenum.test.helper import sdk_get_reply, sdk_sign_and_submit_req


def testSendSchemaMultipleAttribs(looper, sdk_pool_handle, sdk_wallet_trust_anchor):

    wallet_handle, identifier = sdk_wallet_trust_anchor

    schema_json, _ = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_trust_anchor)
    _, schema_json = looper.loop.run_until_complete(
        issuer_create_schema(identifier, "name=Degree", "1.0", json.dumps(["attrib1","attrib2","attrib3"])))

    request = looper.loop.run_until_complete(build_schema_request(identifier, schema_json))

    return schema_json, \
           sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trust_anchor, request))[1]


def test_send_schema_one_attrib(be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)
    do('send SCHEMA name=Degree2 version=1.1 keys=attrib1',
       expect=SCHEMA_ADDED, within=5)


def test_can_not_send_same_schema(be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)
    do('send SCHEMA name=Degree3 version=1.3 keys=attrib1',
       expect=SCHEMA_ADDED, within=5)
    do('send SCHEMA name=Degree3 version=1.3 keys=attrib1',
       expect=SCHEMA_NOT_ADDED_DUPLICATE, within=5)