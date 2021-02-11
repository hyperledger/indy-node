from indy_common.constants import START
from indy_node.test.pool_restart.test_pool_restart import pool_restart_now


def test_pool_restart_now_with_empty_datetime(
        sdk_pool_handle, sdk_wallet_trustee, looper, tdir, tconf, txnPoolNodeSet):
    pool_restart_now(sdk_pool_handle, sdk_wallet_trustee, looper,
                     tdir, tconf, START, "", use_time=False)
