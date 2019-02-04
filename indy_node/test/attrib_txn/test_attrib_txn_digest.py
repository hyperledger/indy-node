import json

import pytest
from indy.ledger import build_attrib_request, sign_request

from indy_common.types import Request
from plenum.common.txn_util import reqToTxn, get_digest
from plenum.test.helper import sdk_set_protocol_version


@pytest.fixture(scope="module")
def req_json(looper, sdk_wallet_steward):
    sdk_set_protocol_version(looper)
    wallet_handle, identifier = sdk_wallet_steward
    raw = json.dumps({'answer': 42})
    return looper.loop.run_until_complete(
        build_attrib_request(identifier, identifier, raw=raw, xhash=None, enc=None))


@pytest.fixture(scope="module")
def req(req_json, looper, sdk_wallet_steward):
    wallet_handle, identifier = sdk_wallet_steward
    req_signed = looper.loop.run_until_complete(sign_request(wallet_handle, identifier, req_json))
    return Request(**json.loads(req_signed))


def test_attrib_txn_digest_req_json(req_json, req):
    txn = reqToTxn(req_json)
    assert get_digest(txn) == req.digest


def test_attrib_txn_digest_req_dict(req):
    txn = reqToTxn(req.as_dict)
    assert get_digest(txn) == req.digest


def test_attrib_txn_digest_req_instance(req):
    txn = reqToTxn(req)
    assert get_digest(txn) == req.digest
