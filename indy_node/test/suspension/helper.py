from plenum.test.helper import sdk_sign_and_submit_op, sdk_get_and_check_replies


def sdk_suspend_role(looper, sdk_pool_handle, sdk_wallet_sender, susp_did):
    op = {'type': '1',
          'dest': susp_did,
          'role': None}
    req = sdk_sign_and_submit_op(looper, sdk_pool_handle, sdk_wallet_sender, op)
    sdk_get_and_check_replies(looper, [req])
