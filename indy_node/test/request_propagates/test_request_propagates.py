import json

import pytest
from indy.anoncreds import issuer_create_schema, issuer_create_and_store_credential_def
from indy.ledger import build_attrib_request, sign_request, build_schema_request, build_cred_def_request, \
    build_nym_request, build_get_schema_request, parse_get_schema_response

from indy_node.test.helper import createHalfKeyIdentifierAndAbbrevVerkey
from indy_common.types import Request
from indy_node.test.api.helper import sdk_write_schema, build_rs_schema_request
from plenum.common.messages.node_messages import Propagate
from plenum.common.types import f
from plenum.server.message_handlers import PropagateHandler
from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_reply


@pytest.fixture(scope="module")
def node(nodeSet):
    return nodeSet[0]


def emulate_received(node, msg):
    return node.nodestack.deserializeMsg(
        node.nodestack.sign_and_serialize(msg)
    )


@pytest.fixture(scope="module", params=["ATTRIB", "SCHEMA", "RS_SCHEMA", "CLAIM_DEF", "NYM"])
def req(request, looper, sdk_pool_handle, sdk_wallet_steward):
    wallet_handle, identifier = sdk_wallet_steward
    if request.param == "ATTRIB":
        raw = json.dumps({'answer': 42})
        request_json = looper.loop.run_until_complete(
            build_attrib_request(identifier, identifier, raw=raw, xhash=None, enc=None))
    elif request.param == "SCHEMA":
        _, schema_json = looper.loop.run_until_complete(
            issuer_create_schema(identifier, "name", "1.0", json.dumps(["first", "last"])))
        request_json = looper.loop.run_until_complete(build_schema_request(identifier, schema_json))
    elif request.param == "RS_SCHEMA":
        rs_schema = {'@id': "fakeId234e", '@type': "0od"}
        request_json = build_rs_schema_request(identifier, rs_schema, "ISO18023_Drivers_License", "1.1")
    elif request.param == "CLAIM_DEF":
        schema_json, _ = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_steward)
        schema_id = json.loads(schema_json)['id']

        request = looper.loop.run_until_complete(build_get_schema_request(identifier, schema_id))
        reply = sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, request))[1]
        _, schema_json = looper.loop.run_until_complete(parse_get_schema_response(json.dumps(reply)))

        _, definition_json = looper.loop.run_until_complete(issuer_create_and_store_credential_def(
            wallet_handle, identifier, schema_json, "some_tag", "CL", json.dumps({"support_revocation": True})))
        request_json = looper.loop.run_until_complete(build_cred_def_request(identifier, definition_json))
    elif request.param == "NYM":
        idr, verkey = createHalfKeyIdentifierAndAbbrevVerkey()
        request_json = looper.loop.run_until_complete(build_nym_request(identifier, idr, verkey, None, None))

    req_signed = looper.loop.run_until_complete(sign_request(wallet_handle, identifier, request_json))
    return Request(**json.loads(req_signed))


def test_propagate_request(looper, node, sdk_wallet_steward, req):
    # Emulate Received PROPAGATE with the req
    propagate = Propagate(req.as_dict, "client_name")
    msg = emulate_received(node, propagate)

    # Create a new (requested) Propagate from the received data
    ph = PropagateHandler(node)
    kwargs = {f.DIGEST.nm: req.digest}
    received_propagate = ph.create(msg, **kwargs)
    assert received_propagate == propagate
