from plenum.test import waits
from indy_client.test.helper import checkRejects, checkNacks
from plenum.test.helper import sdk_sign_and_submit_op, sdk_get_and_check_replies
from stp_core.loop.eventually import eventually


def checkIdentityRequestFailed(looper, client, req, cause):
    timeout = waits.expectedReqRejectQuorumTime()
    # TODO: Just for now, better to have a generic negative response checker
    try:
        looper.run(eventually(checkRejects,
                              client,
                              req.reqId,
                              cause, retryWait=1, timeout=timeout))
    except AssertionError:
        looper.run(eventually(checkNacks,
                              client,
                              req.reqId,
                              cause, retryWait=1, timeout=timeout))


def checkIdentityRequestSucceed(looper, actingClient, actingWallet, idr):
    def chk():
        assert actingWallet.getTrustAnchoredIdentity(idr).seqNo is not None

    timeout = waits.expectedTransactionExecutionTime(
        len(actingClient.nodeReg)
    )
    looper.run(eventually(chk, retryWait=1, timeout=timeout))


def sdk_suspend_role(looper, sdk_pool_handle, sdk_wallet_sender, susp_did):
    op = {'type': '1',
          'dest': susp_did,
          'role': None}
    req = sdk_sign_and_submit_op(looper, sdk_pool_handle, sdk_wallet_sender, op)
    sdk_get_and_check_replies(looper, [req])
