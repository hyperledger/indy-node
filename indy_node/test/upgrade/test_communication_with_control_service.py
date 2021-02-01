import asyncio
from datetime import datetime

import pytest
from stp_core.loop.eventually import eventuallySoon

from indy_node.server.upgrade_log import UpgradeLogData
from indy_node.server.upgrader import Upgrader, UpgradeMessage

from indy_node.test.upgrade.helper import bumpedVersion


async def _createServer(host, port):
    """
    Create async server that listens host:port, reads client request and puts
    value to some future that can be used then for checks

    :return: reference to server and future for request
    """
    indicator = asyncio.Future()

    async def _handle(reader, writer):
        raw = await reader.readline()
        request = raw.decode("utf-8")
        indicator.set_result(request)
    server = await asyncio.start_server(_handle, host, port)
    return server, indicator


def _stopServer(server):
    def _stop(x):
        print('Closing server')
        server.close()
    return _stop


def _checkFuture(future):
    """
    Wrapper for futures that lets checking of their status using 'eventually'
    """
    def _check():
        if future.cancelled():
            return None
        if future.done():
            return future.result()
        raise Exception()
    return _check


@pytest.mark.upgrade
def test_schedule_node_upgrade(tconf, nodeSet):
    """
    Tests that upgrade scheduling works. For that it starts mock
    control service, schedules upgrade for near future and then checks that
    service received notification.
    """
    loop = asyncio.get_event_loop()
    server, indicator = loop.run_until_complete(
        _createServer(
            host=tconf.controlServiceHost,
            port=tconf.controlServicePort
        )
    )
    indicator.add_done_callback(_stopServer(server))

    node = nodeSet[0]

    # ATTENTION! nodeId and ledger must not be None, but there
    # we do not call methods that use them, so we can pass None
    # We do it because node from nodeSet is some testable object, not real
    # node, so it has no nodeId and ledger that we can use
    upgrader = Upgrader(nodeId=None,
                        nodeName=None,
                        dataDir=node.dataLocation,
                        config=tconf,
                        ledger=None)
    version = bumpedVersion()
    ev_data = UpgradeLogData(
        datetime.utcnow(), version, 'some_id', tconf.UPGRADE_ENTRY)
    upgrader._callUpgradeAgent(ev_data, 1000)

    result = loop.run_until_complete(eventuallySoon(_checkFuture(indicator)))
    expectedResult = UpgradeMessage(version, tconf.UPGRADE_ENTRY)
    assert result == expectedResult.toJson()


# def test_cancel_node_upgrade():
#     """
#     Test cancellation of scheduled upgrades. This test schedules upgrade for
#     unreachable moment in future and then tries to cancel that
#     before timeout
#     """
#     loop = asyncio.get_event_loop()
#     farMomentInFuture = time.time() + 10000
#     up = node_control_tools.scheduleNodeUpgrade(farMomentInFuture, version)
#     upgrade = loop.run_until_complete(up)  # type: asyncio.Future
#     node_control_tools.cancelNodeUpgrade(version)
#     loop.run_until_complete(eventuallySoon(_checkFuture(upgrade)))
