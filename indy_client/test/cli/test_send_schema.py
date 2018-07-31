import json

from indy.anoncreds import issuer_create_schema
from indy.ledger import build_schema_request
from plenum.common.exceptions import RequestRejectedException

from indy_common.auth import Authoriser

from plenum.test.helper import sdk_sign_and_submit_req, sdk_get_and_check_replies, sdk_get_bad_response

from indy_client.test.cli.constants import SCHEMA_ADDED, SCHEMA_NOT_ADDED_DUPLICATE


def test_send_schema_multiple_attribs(be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)
    do('send SCHEMA name=Degree version=1.0 keys=attrib1,attrib2,attrib3',
       expect=SCHEMA_ADDED, within=5)


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


def test_client_can_send_schema(looper,
                                txnPoolNodeSet,
                                sdk_wallet_client,
                                sdk_wallet_trust_anchor,
                                sdk_pool_handle,
                                tconf):
    # We need to reset authorization map to set new authorization rules
    Authoriser.auth_map = None

    OLD_WRITES_REQUIRE_TRUST_ANCHOR = tconf.WRITES_REQUIRE_TRUST_ANCHOR
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = False

    # Trust anchor can create schema in any case
    _, identifier = sdk_wallet_trust_anchor
    _, schema_json = looper.loop.run_until_complete(
        issuer_create_schema(identifier, "name", "1.0", json.dumps(["first", "last"])))
    request = looper.loop.run_until_complete(build_schema_request(identifier, schema_json))
    sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trust_anchor, request)])

    # Client can create schema if WRITES_REQUIRE_TRUST_ANCHOR flag set to False
    _, identifier = sdk_wallet_client
    _, schema_json = looper.loop.run_until_complete(
        issuer_create_schema(identifier, "name", "1.0", json.dumps(["first", "last"])))
    request = looper.loop.run_until_complete(build_schema_request(identifier, schema_json))
    sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_client, request)])

    Authoriser.auth_map = None
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = OLD_WRITES_REQUIRE_TRUST_ANCHOR


def test_client_cant_send_schema(looper,
                                 txnPoolNodeSet,
                                 sdk_wallet_client,
                                 sdk_wallet_trust_anchor,
                                 sdk_pool_handle,
                                 tconf):
    # We need to reset authorization map to set new authorization rules
    Authoriser.auth_map = None

    OLD_WRITES_REQUIRE_TRUST_ANCHOR = tconf.WRITES_REQUIRE_TRUST_ANCHOR
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = True

    # Trust anchor can create schema in any case
    _, identifier = sdk_wallet_trust_anchor
    _, schema_json = looper.loop.run_until_complete(
        issuer_create_schema(identifier, "another_name", "2.0", json.dumps(["first", "last"])))
    request = looper.loop.run_until_complete(build_schema_request(identifier, schema_json))
    sdk_get_and_check_replies(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_trust_anchor, request)])

    # Client cant create schema if WRITES_REQUIRE_TRUST_ANCHOR flag set to True
    _, identifier = sdk_wallet_client
    _, schema_json = looper.loop.run_until_complete(
        issuer_create_schema(identifier, "another_name", "2.0", json.dumps(["first", "last"])))
    request = looper.loop.run_until_complete(build_schema_request(identifier, schema_json))
    sdk_get_bad_response(looper, [sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_client, request)],
                         RequestRejectedException, 'None role cannot add schema')

    Authoriser.auth_map = None
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = OLD_WRITES_REQUIRE_TRUST_ANCHOR
