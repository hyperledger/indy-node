import json

from indy.ledger import build_attrib_request
from indy_node.test.api.helper import validate_write_reply, validate_attrib_txn
from plenum.test.helper import sdk_get_reply, sdk_sign_and_submit_req
from hashlib import sha256


def execute_attrib_txn(looper, sdk_pool_handle, sdk_wallet_steward, xhash, raw, enc):
    _, identifier = sdk_wallet_steward
    request = looper.loop.run_until_complete(build_attrib_request(identifier, identifier, xhash, raw, enc))
    return sdk_get_reply(looper, sdk_sign_and_submit_req(sdk_pool_handle, sdk_wallet_steward, request))[1]


def test_attrib_xhash_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    xhash = sha256("Hello, world".encode()).hexdigest()
    reply = execute_attrib_txn(looper, sdk_pool_handle, sdk_wallet_steward, xhash, None, None)

    validate_write_reply(reply)
    validate_attrib_txn(reply['result']['txn'])
    assert reply['result']['txn']['data']['hash'] == xhash


def test_attrib_raw_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    raw = json.dumps({'answer': 42})
    reply = execute_attrib_txn(looper, sdk_pool_handle, sdk_wallet_steward, None, raw, None)

    validate_write_reply(reply)
    validate_attrib_txn(reply['result']['txn'])
    assert json.loads(reply['result']['txn']['data']['raw']) == json.loads(raw)


def test_attrib_enc_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    enc = "amgine"
    reply = execute_attrib_txn(looper, sdk_pool_handle, sdk_wallet_steward, None, None, enc)

    validate_write_reply(reply)
    validate_attrib_txn(reply['result']['txn'])
    assert reply['result']['txn']['data']['enc'] == enc
