import pytest
from stp_core.loop.eventually import eventually

whitelist = ['Failed to upgrade node', 'Failed to send update request!']


@pytest.fixture(scope="module")
def dontClearNode(nodeSet):
    for node in nodeSet:
        node.cleanupOnStopping = False


def testTimeoutWorks(nodeSet, looper, dontClearNode, validUpgradeSent,
                     upgradeScheduled):
    """
    Checks that after some timeout upgrade is marked as failed if
    it not started
    """

    pending = {node.name for node in nodeSet}

    def chk():
        nonlocal pending
        assert len(pending) == 0

    def callback(oldCallback, nodeName):
        def f():
            print("_upgradeFailedCallback called of {}'s upgrader".format(nodeName))
            oldCallback()
            nonlocal pending
            pending.remove(nodeName)
        return f

    for node in nodeSet:
        oldCallback = node.upgrader._upgradeFailedCallback
        node.upgrader._upgradeFailedCallback = \
            callback(oldCallback, node.name)
        print(node.upgrader.scheduledUpgrade)

    looper.run(eventually(chk,
                          retryWait=10,
                          timeout=90))
