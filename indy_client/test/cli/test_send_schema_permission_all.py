import json

import pytest
from indy.anoncreds import issuer_create_schema
from indy.ledger import build_schema_request

from indy_common.auth import Authoriser
from plenum.test.helper import sdk_get_and_check_replies, sdk_sign_and_submit_req


@pytest.fixture(scope="module")
def tconf(tconf):
    # We need to reset authorization map to set new authorization rules
    Authoriser.auth_map = None
    OLD_WRITES_REQUIRE_TRUST_ANCHOR = tconf.WRITES_REQUIRE_TRUST_ANCHOR
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = False

    yield tconf

    tconf.WRITES_REQUIRE_TRUST_ANCHOR = OLD_WRITES_REQUIRE_TRUST_ANCHOR
    Authoriser.auth_map = None


def test_client_can_send_schema(looper,
                                txnPoolNodeSet,
                                sdk_wallet_client,
                                sdk_wallet_trust_anchor,
                                sdk_pool_handle,
                                tconf):
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
