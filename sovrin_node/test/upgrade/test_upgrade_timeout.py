import pytest
from stp_core.loop.eventually import eventually
from sovrin_node.test.upgrade.test_pool_upgrade \
    import validUpgradeSent, upgradeScheduled

whitelist = ['Failed to upgrade node', 'Failed to send update request!']


def testTimeoutWorks(nodeSet, looper, validUpgradeSent, upgradeScheduled):
    """
    Checks that after some timeout upgrade is marked as failed if
    it not started
    """

    import asyncio
    completionFuture = asyncio.Future()

    def callback(oldCallback, completionFuture):
        def f():
            completionFuture.set_result(True)
            oldCallback()
        return f

    for node in nodeSet:
        oldCallback = node.upgrader._upgradeFailedCallback
        node.upgrader._upgradeFailedCallback = \
            callback(oldCallback, completionFuture)
        print(node.upgrader.scheduledUpgrade)
    print("ZZZZZZZ")

    looper.run(eventually(lambda x: completionFuture.result(),
                          nodeSet,
                          retryWait=20,
                          timeout=60))
