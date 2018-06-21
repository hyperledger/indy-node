from indy_node.test.api.helper import validate_write_reply, validate_schema_txn, sdk_write_schema


def test_schema_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    _, reply = sdk_write_schema(looper, sdk_pool_handle, sdk_wallet_steward)
    validate_write_reply(reply)
    validate_schema_txn(reply['result']['txn'])
