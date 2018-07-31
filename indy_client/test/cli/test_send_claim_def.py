import json

from indy_common.auth import Authoriser

from indy_client.test.cli.constants import SCHEMA_ADDED, CLAIM_DEF_ADDED
from indy_client.test.cli.helper import getSeqNoFromCliOutput
from plenum.common.exceptions import RequestRejectedException
from plenum.test.helper import sdk_send_and_check, sdk_sign_request_from_dict, sdk_send_signed_requests, \
    sdk_get_bad_response

from indy_node.test.anon_creds.conftest import claim_def


def test_send_claim_def_succeeds(
        be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)

    do('send SCHEMA name=Degree version=1.0'
       ' keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date',
       expect=SCHEMA_ADDED,
       within=5)

    schemaTxnSeqNo = getSeqNoFromCliOutput(trusteeCli)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect=CLAIM_DEF_ADDED,
       mapper={'ref': schemaTxnSeqNo},
       within=239)


def test_send_claim_def_fails_if_ref_is_seqno_of_non_schema_txn(
        be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)

    do('send SCHEMA name=Degree version=1.1'
       ' keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date',
       expect=SCHEMA_ADDED,
       within=5)

    schemaTxnSeqNo = getSeqNoFromCliOutput(trusteeCli)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect=CLAIM_DEF_ADDED,
       mapper={'ref': schemaTxnSeqNo},
       within=239)

    firstClaimDefSeqNo = getSeqNoFromCliOutput(trusteeCli)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect='Schema with seqNo {ref} not found',
       mapper={'ref': firstClaimDefSeqNo},
       within=5)


def test_send_claim_def_fails_if_ref_is_not_existing_seqno(
        be, do, poolNodesStarted, trusteeCli):
    be(trusteeCli)

    do('send SCHEMA name=Degree version=1.2'
       ' keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date',
       expect=SCHEMA_ADDED, within=5)

    schemaTxnSeqNo = getSeqNoFromCliOutput(trusteeCli)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect='Schema with seqNo {ref} not found',
       mapper={'ref': schemaTxnSeqNo + 1},
       within=5)


def test_update_claim_def_for_same_schema_and_signature_type(
        be, do, trusteeCli):
    be(trusteeCli)

    do('send SCHEMA name=Degree version=1.3'
       ' keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date',
       expect=SCHEMA_ADDED,
       within=5)

    schemaTxnSeqNo = getSeqNoFromCliOutput(trusteeCli)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect=CLAIM_DEF_ADDED,
       mapper={'ref': schemaTxnSeqNo},
       within=239)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect=CLAIM_DEF_ADDED,
       mapper={'ref': schemaTxnSeqNo},
       within=239)


def test_can_send_same_claim_def_by_different_issuers(
        be, do, poolNodesStarted, trusteeCli, newStewardCli):
    be(trusteeCli)

    do('send SCHEMA name=Degree version=1.4'
       ' keys=undergrad,last_name,first_name,birth_date,postgrad,expiry_date',
       expect=SCHEMA_ADDED,
       within=5)

    schemaTxnSeqNo = getSeqNoFromCliOutput(trusteeCli)

    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect=CLAIM_DEF_ADDED,
       mapper={'ref': schemaTxnSeqNo},
       within=239)

    be(newStewardCli)
    do('send CLAIM_DEF ref={ref} signature_type=CL',
       expect=CLAIM_DEF_ADDED,
       mapper={'ref': schemaTxnSeqNo},
       within=239)


def test_client_can_send_claim_def(looper,
                                   txnPoolNodeSet,
                                   sdk_wallet_client,
                                   sdk_wallet_trust_anchor,
                                   sdk_pool_handle,
                                   claim_def,
                                   tconf):
    # We need to reset authorization map to set new authorization rules
    Authoriser.auth_map = None

    OLD_WRITES_REQUIRE_TRUST_ANCHOR = tconf.WRITES_REQUIRE_TRUST_ANCHOR
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = False

    # Trust anchor can create claim_def in any case
    req = sdk_sign_request_from_dict(looper, sdk_wallet_trust_anchor, claim_def)
    sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)

    # Client can create claim_def if WRITES_REQUIRE_TRUST_ANCHOR flag set to False
    req = sdk_sign_request_from_dict(looper, sdk_wallet_client, claim_def)
    sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)

    Authoriser.auth_map = None
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = OLD_WRITES_REQUIRE_TRUST_ANCHOR


def test_client_cant_send_claim_def(looper,
                                    txnPoolNodeSet,
                                    sdk_wallet_client,
                                    sdk_wallet_trust_anchor,
                                    sdk_pool_handle,
                                    claim_def,
                                    tconf):
    # We need to reset authorization map to set new authorization rules
    Authoriser.auth_map = None

    OLD_WRITES_REQUIRE_TRUST_ANCHOR = tconf.WRITES_REQUIRE_TRUST_ANCHOR
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = True

    # Trust anchor can create claim_def in any case
    req = sdk_sign_request_from_dict(looper, sdk_wallet_trust_anchor, claim_def)
    sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)

    # Client cant send create if WRITES_REQUIRE_TRUST_ANCHOR flag set to True
    req = sdk_sign_request_from_dict(looper, sdk_wallet_client, claim_def)
    req = sdk_send_signed_requests(sdk_pool_handle, [json.dumps(req)])
    sdk_get_bad_response(looper, req, RequestRejectedException, 'None role cannot add claim def')

    Authoriser.auth_map = None
    tconf.WRITES_REQUIRE_TRUST_ANCHOR = OLD_WRITES_REQUIRE_TRUST_ANCHOR
