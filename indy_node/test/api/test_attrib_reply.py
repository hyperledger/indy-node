import json

from indy.ledger import build_attrib_request, sign_request, submit_request
from indy_node.test.api.helper import validate_write_reply, validate_attrib_txn
from hashlib import sha256


def execute_attrib_txn(looper, sdk_pool_handle, sdk_wallet_steward, xhash, raw, enc):
    wallet_handle, identifier = sdk_wallet_steward

    request = looper.loop.run_until_complete(build_attrib_request(identifier, identifier, xhash, raw, enc))
    req_signed = looper.loop.run_until_complete(sign_request(wallet_handle, identifier, request))
    return json.loads(looper.loop.run_until_complete(submit_request(sdk_pool_handle, req_signed)))


def test_attrib_xhash_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    reply = execute_attrib_txn(looper, sdk_pool_handle, sdk_wallet_steward,
                               sha256("Hello, world".encode()).hexdigest(), None, None)

    validate_write_reply(reply)
    validate_attrib_txn(reply['result']['txn'])


def test_attrib_raw_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    reply = execute_attrib_txn(looper, sdk_pool_handle, sdk_wallet_steward,
                               None, json.dumps({'answer': 42}), None)

    validate_write_reply(reply)
    validate_attrib_txn(reply['result']['txn'])


def test_attib_enc_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    reply = execute_attrib_txn(looper, sdk_pool_handle, sdk_wallet_steward,
                               None, None, "amgine")

    validate_write_reply(reply)
    validate_attrib_txn(reply['result']['txn'])
