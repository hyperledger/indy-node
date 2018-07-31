import json
import pytest

from indy_common.auth import Authoriser
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_and_check

from indy_node.test.anon_creds.conftest import claim_def


@pytest.fixture(scope="module")
def tconf(tconf):
    # We need to reset authorization map to set new authorization rules
    Authoriser.auth_map = None
    OLD_WRITES_REQUIRE_TRUST_ANCHOR = tconf.WRITES_REQUIRE_TRUST_ANCHOR
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = False

    yield tconf

    tconf.WRITES_REQUIRE_TRUST_ANCHOR = OLD_WRITES_REQUIRE_TRUST_ANCHOR
    Authoriser.auth_map = None


def test_client_can_send_claim_def(looper,
                                   txnPoolNodeSet,
                                   sdk_wallet_client,
                                   sdk_wallet_trust_anchor,
                                   sdk_pool_handle,
                                   claim_def,
                                   tconf):
    # Trust anchor can create claim_def in any case
    req = sdk_sign_request_from_dict(looper, sdk_wallet_trust_anchor, claim_def)
    sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)

    # Client can create claim_def if WRITES_REQUIRE_TRUST_ANCHOR flag set to False
    req = sdk_sign_request_from_dict(looper, sdk_wallet_client, claim_def)
    sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)
