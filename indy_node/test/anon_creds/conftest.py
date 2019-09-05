import pytest
import time
import json

from indy.anoncreds import issuer_create_and_store_credential_def
from indy.ledger import build_cred_def_request

from indy_common.state.domain import make_state_path_for_claim_def
from indy_node.test.anon_creds.helper import get_cred_def_id, create_revoc_reg, create_revoc_reg_entry
from plenum.common.util import randomString
from indy_common.constants import REVOC_REG_ENTRY, REVOC_REG_DEF_ID, ISSUED, \
    REVOKED, PREV_ACCUM, ACCUM, REVOC_REG_DEF, ISSUANCE_BY_DEFAULT, \
    CRED_DEF_ID, VALUE, TAG, ISSUANCE_ON_DEMAND, ID, \
    TXN_TYPE, REVOC_TYPE, ISSUANCE_TYPE, MAX_CRED_NUM, TAILS_HASH, TAILS_LOCATION, PUBLIC_KEYS, \
    GET_REVOC_REG, TIMESTAMP, CLAIM_DEF_SCHEMA_REF, CLAIM_DEF_SIGNATURE_TYPE, \
    CLAIM_DEF_TAG
from indy_common.types import Request
from indy_common.state import domain
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_and_check, sdk_sign_and_submit_req, \
    sdk_get_and_check_replies
from plenum.common.txn_util import reqToTxn, append_txn_metadata
from plenum.common.types import f, OPERATION

from plenum.test.conftest import sdk_wallet_client
from indy_node.test.schema.test_send_get_schema import send_schema_req

CRED_DEF_VERSION = '1.0'
SCHEMA_VERSION = '1.0'


@pytest.fixture(scope="module")
def claim_def(looper, sdk_wallet_handle, sdk_wallet_steward, send_schema_req):
    schema = json.loads(send_schema_req[0])
    tag = 'some_tag'
    schema_seq_no = send_schema_req[1]['result']['txnMetadata']['seqNo']
    schema['seqNo'] = schema_seq_no

    definition_id, definition_json = \
        looper.loop.run_until_complete(issuer_create_and_store_credential_def(
            sdk_wallet_handle, sdk_wallet_steward[1], json.dumps(schema),
            tag, "CL", json.dumps({"support_revocation": True})))
    cred_def = looper.loop.run_until_complete(build_cred_def_request(sdk_wallet_steward[1], definition_json))
    return json.loads(cred_def)['operation']


@pytest.fixture(scope="module")
def send_claim_def(looper,
                   txnPoolNodeSet,
                   sdk_wallet_steward,
                   sdk_pool_handle,
                   claim_def):
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, claim_def)
    rep = sdk_send_and_check([json.dumps(req)], looper, txnPoolNodeSet, sdk_pool_handle)[0]
    return rep


@pytest.fixture(scope="module")
def send_revoc_reg_def(looper, sdk_wallet_handle, sdk_pool_handle, sdk_wallet_steward, send_claim_def):
    revoc_reg = create_revoc_reg(looper, sdk_wallet_handle, sdk_wallet_steward[1], randomString(5),
                                 get_cred_def_id(send_claim_def[0][f.IDENTIFIER.nm],
                                                 send_claim_def[0]['operation']['ref'],
                                                 send_claim_def[0]['operation']['tag']),
                                 ISSUANCE_BY_DEFAULT)
    req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, revoc_reg)
    rep = sdk_get_and_check_replies(looper, [req])[0]
    return rep


@pytest.fixture(scope="module")
def send_revoc_reg_entry(looper, sdk_wallet_handle, sdk_pool_handle, sdk_wallet_steward, send_claim_def):
    revoc_reg, revoc_entry = create_revoc_reg_entry(looper, sdk_wallet_handle, sdk_wallet_steward[1], randomString(5),
                                                    get_cred_def_id(send_claim_def[0][f.IDENTIFIER.nm],
                                                                    send_claim_def[0]['operation']['ref'],
                                                                    send_claim_def[0]['operation']['tag']),
                                                    ISSUANCE_BY_DEFAULT)
    req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, revoc_reg)
    revoc_reg = sdk_get_and_check_replies(looper, [req])[0]
    req = sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, revoc_entry)
    revoc_entry = sdk_get_and_check_replies(looper, [req])[0]
    return revoc_reg, revoc_entry


@pytest.fixture(scope="module")
def add_revoc_def_by_default(create_node_and_not_start,
                             looper,
                             sdk_wallet_steward):
    node = create_node_and_not_start
    data = {
        ID: randomString(50),
        TXN_TYPE: REVOC_REG_DEF,
        REVOC_TYPE: "CL_ACCUM",
        TAG: randomString(5),
        CRED_DEF_ID: ":".join(4 * [randomString(10)]),
        VALUE: {
            ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT,
            MAX_CRED_NUM: 1000000,
            TAILS_HASH: randomString(50),
            TAILS_LOCATION: 'http://tails.location.com',
            PUBLIC_KEYS: {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)

    txn = append_txn_metadata(reqToTxn(Request(**req)),
                              txn_time=int(time.time()),
                              seq_no=node.domainLedger.seqNo + 1)
    node.write_manager.update_state(txn)
    return req


def build_revoc_reg_entry_for_given_revoc_reg_def(
        revoc_def_req):
    path = ":".join([revoc_def_req[f.IDENTIFIER.nm],
                     domain.MARKER_REVOC_DEF,
                     revoc_def_req[OPERATION][CRED_DEF_ID],
                     revoc_def_req[OPERATION][REVOC_TYPE],
                     revoc_def_req[OPERATION][TAG]])
    data = {
        REVOC_REG_DEF_ID: path,
        TXN_TYPE: REVOC_REG_ENTRY,
        REVOC_TYPE: revoc_def_req[OPERATION][REVOC_TYPE],
        VALUE: {
            PREV_ACCUM: randomString(10),
            ACCUM: randomString(10),
            ISSUED: [],
            REVOKED: [],
        }
    }
    return data


@pytest.fixture(scope="function")
def build_txn_for_revoc_def_entry_by_default(looper,
                                             sdk_wallet_steward,
                                             add_revoc_def_by_default):
    revoc_def_req = add_revoc_def_by_default
    data = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req)
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return req


@pytest.fixture(scope="module")
def add_revoc_def_by_demand(create_node_and_not_start,
                            looper,
                            sdk_wallet_steward):
    node = create_node_and_not_start
    data = {
        ID: randomString(50),
        TXN_TYPE: REVOC_REG_DEF,
        REVOC_TYPE: "CL_ACCUM",
        TAG: randomString(5),
        CRED_DEF_ID: ":".join(4 * [randomString(10)]),
        VALUE: {
            ISSUANCE_TYPE: ISSUANCE_ON_DEMAND,
            MAX_CRED_NUM: 1000000,
            TAILS_HASH: randomString(50),
            TAILS_LOCATION: 'http://tails.location.com',
            PUBLIC_KEYS: {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)

    txn = append_txn_metadata(reqToTxn(Request(**req)),
                              txn_time=int(time.time()),
                              seq_no=node.domainLedger.seqNo + 1)
    node.write_manager.update_state(txn)
    return req


@pytest.fixture(scope="module")
def build_txn_for_revoc_def_entry_by_demand(looper,
                                            sdk_wallet_steward,
                                            add_revoc_def_by_demand):
    revoc_def_req = add_revoc_def_by_demand
    path = ":".join([revoc_def_req[f.IDENTIFIER.nm],
                     domain.MARKER_REVOC_DEF,
                     revoc_def_req[OPERATION][CRED_DEF_ID],
                     revoc_def_req[OPERATION][REVOC_TYPE],
                     revoc_def_req[OPERATION][TAG]])
    data = {
        REVOC_REG_DEF_ID: path,
        TXN_TYPE: REVOC_REG_ENTRY,
        VALUE: {
            PREV_ACCUM: randomString(10),
            ACCUM: randomString(10),
            ISSUED: [],
            REVOKED: [],
        }
    }

    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return req


@pytest.fixture(scope="module")
def build_revoc_def_by_default(looper, sdk_wallet_steward):
    data = {
        ID: randomString(50),
        TXN_TYPE: REVOC_REG_DEF,
        REVOC_TYPE: "CL_ACCUM",
        TAG: randomString(5),
        CRED_DEF_ID: ":".join(4 * [randomString(10)]),
        VALUE: {
            ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT,
            MAX_CRED_NUM: 1000000,
            TAILS_HASH: randomString(50),
            TAILS_LOCATION: 'http://tails.location.com',
            PUBLIC_KEYS: {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return req


@pytest.fixture(scope="module")
def build_revoc_def_by_endorser(looper, sdk_wallet_endorser):
    data = {
        ID: randomString(50),
        TXN_TYPE: REVOC_REG_DEF,
        REVOC_TYPE: "CL_ACCUM",
        TAG: randomString(5),
        CRED_DEF_ID: ":".join(4 * [randomString(10)]),
        VALUE: {
            ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT,
            MAX_CRED_NUM: 1000000,
            TAILS_HASH: randomString(50),
            TAILS_LOCATION: 'http://tails.location.com',
            PUBLIC_KEYS: {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_endorser, data)
    return req


@pytest.fixture(scope="module")
def build_revoc_def_by_steward(looper, sdk_wallet_steward):
    data = {
        ID: randomString(50),
        TXN_TYPE: REVOC_REG_DEF,
        REVOC_TYPE: "CL_ACCUM",
        TAG: randomString(5),
        CRED_DEF_ID: ":".join(4 * [randomString(10)]),
        VALUE: {
            ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT,
            MAX_CRED_NUM: 1000000,
            TAILS_HASH: randomString(50),
            TAILS_LOCATION: 'http://tails.location.com',
            PUBLIC_KEYS: {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return req


def build_revoc_def_random(looper, sdk_wallet):
    data = {
        ID: randomString(50),
        TXN_TYPE: REVOC_REG_DEF,
        REVOC_TYPE: "CL_ACCUM",
        TAG: randomString(5),
        CRED_DEF_ID: ":".join(4 * [randomString(10)]),
        VALUE: {
            ISSUANCE_TYPE: ISSUANCE_BY_DEFAULT,
            MAX_CRED_NUM: 1000000,
            TAILS_HASH: randomString(50),
            TAILS_LOCATION: 'http://tails.location.com',
            PUBLIC_KEYS: {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet, data)
    return req


@pytest.fixture(scope="module")
def build_revoc_def_by_demand(looper, sdk_wallet_steward):
    data = {
        ID: randomString(50),
        TXN_TYPE: REVOC_REG_DEF,
        REVOC_TYPE: "CL_ACCUM",
        TAG: randomString(5),
        CRED_DEF_ID: ":".join(4 * [randomString(10)]),
        VALUE: {
            ISSUANCE_TYPE: ISSUANCE_ON_DEMAND,
            MAX_CRED_NUM: 1000000,
            TAILS_HASH: randomString(50),
            TAILS_LOCATION: 'http://tails.location.com',
            PUBLIC_KEYS: {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return req


@pytest.fixture(scope="module")
def send_revoc_reg_def_by_default(looper,
                                  txnPoolNodeSet,
                                  sdk_wallet_steward,
                                  sdk_pool_handle,
                                  send_claim_def,
                                  build_revoc_def_by_default):
    _, author_did = sdk_wallet_steward
    claim_def_req = send_claim_def[0]
    revoc_reg = build_revoc_def_by_default
    revoc_reg['operation'][CRED_DEF_ID] = \
        make_state_path_for_claim_def(author_did,
                                      str(claim_def_req['operation'][CLAIM_DEF_SCHEMA_REF]),
                                      claim_def_req['operation'][CLAIM_DEF_SIGNATURE_TYPE],
                                      claim_def_req['operation'][CLAIM_DEF_TAG]
                                      ).decode()
    revoc_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, revoc_reg['operation'])
    _, revoc_reply = sdk_send_and_check([json.dumps(revoc_req)], looper, txnPoolNodeSet, sdk_pool_handle)[0]
    return revoc_req, revoc_reply


@pytest.fixture(scope="module")
def send_revoc_reg_def_by_demand(looper,
                                 txnPoolNodeSet,
                                 sdk_wallet_steward,
                                 sdk_pool_handle,
                                 send_claim_def,
                                 build_revoc_def_by_demand):
    _, author_did = sdk_wallet_steward
    claim_def_req = send_claim_def[0]
    revoc_reg = build_revoc_def_by_demand
    revoc_reg['operation'][CRED_DEF_ID] = make_state_path_for_claim_def(author_did,
                                                                        str(claim_def_req['operation'][
                                                                                CLAIM_DEF_SCHEMA_REF]),
                                                                        claim_def_req['operation'][
                                                                            CLAIM_DEF_SIGNATURE_TYPE],
                                                                        claim_def_req['operation'][CLAIM_DEF_TAG]
                                                                        ).decode()
    revoc_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, revoc_reg['operation'])
    sdk_send_and_check([json.dumps(revoc_req)], looper, txnPoolNodeSet, sdk_pool_handle)
    return revoc_req


@pytest.fixture(scope="module")
def send_revoc_reg_entry_by_default(looper,
                                    txnPoolNodeSet,
                                    sdk_wallet_steward,
                                    sdk_pool_handle,
                                    send_revoc_reg_def_by_default):
    revoc_def_req, _ = send_revoc_reg_def_by_default
    rev_reg_entry = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req)
    rev_reg_entry[VALUE][REVOKED] = [1, 2, 3, 4, 5]
    del rev_reg_entry[VALUE][PREV_ACCUM]
    rev_entry_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, rev_reg_entry)
    reg_entry_replies = sdk_send_and_check([json.dumps(rev_entry_req)],
                                           looper,
                                           txnPoolNodeSet,
                                           sdk_pool_handle)
    return reg_entry_replies[0]


@pytest.fixture(scope="module")
def send_revoc_reg_entry_by_demand(looper,
                                   txnPoolNodeSet,
                                   sdk_wallet_steward,
                                   sdk_pool_handle,
                                   send_revoc_reg_def_by_demand):
    revoc_def_req = send_revoc_reg_def_by_demand
    rev_reg_entry = build_revoc_reg_entry_for_given_revoc_reg_def(revoc_def_req)
    rev_reg_entry[VALUE][ISSUED] = [1, 2, 3, 4, 5]
    del rev_reg_entry[VALUE][PREV_ACCUM]
    rev_entry_req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, rev_reg_entry)
    reg_entry_replies = sdk_send_and_check([json.dumps(rev_entry_req)],
                                           looper,
                                           txnPoolNodeSet,
                                           sdk_pool_handle)
    return reg_entry_replies[0]


@pytest.fixture(scope="module")
def create_node_and_not_start(create_node_and_not_start):
    create_node_and_not_start.bootstrapper.upload_states()
    return create_node_and_not_start