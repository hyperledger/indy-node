import pytest

from indy_client.test import waits
from stp_core.loop.eventually import eventually

from indy_client.test.cli.helper import checkConnectedToEnv, prompt_is


@pytest.fixture(scope="module")
def alice(aliceCLI):
    return aliceCLI


def test_disconnect_when_not_connected(alice, be, do):
    be(alice)
    do(None, expect=prompt_is("indy"))
    do('disconnect', within=1, expect=['Not connected to any environment.'])
    do(None, expect=prompt_is("indy"))


@pytest.fixture(scope="module")
def alice_connected(alice, be, do, poolNodesCreated):
    be(alice)
    do(None, expect=prompt_is("indy"))
    do('connect sandbox', within=5, expect=["Connected to sandbox"])
    do(None, expect=prompt_is("indy@sandbox"))


def test_connect_to_test(alice_connected):
    pass


@pytest.fixture(scope="module")
def alice_disconnected(alice, be, do, alice_connected):
    be(alice)
    do(None, expect=prompt_is("indy@sandbox"))
    do('disconnect', within=1, expect=[
        'Disconnecting from sandbox ...',
        'Disconnected from sandbox'
    ])
    do(None, expect=prompt_is("indy"))


def test_disconnect_when_connected(do, be, alice_disconnected):
    pass


def testConnectEnv(poolNodesCreated, looper, notConnectedStatus):
    poolCLI = poolNodesCreated
    notConnectedMsgs = notConnectedStatus
    # Done to initialise a wallet.
    poolCLI.enterCmd("new key")

    poolCLI.enterCmd("status")
    for msg in notConnectedMsgs:
        assert msg in poolCLI.lastCmdOutput

    poolCLI.enterCmd("connect dummy")
    assert "Unknown environment dummy" in poolCLI.lastCmdOutput

    poolCLI.enterCmd("connect sandbox")
    assert "Connecting to sandbox" in poolCLI.lastCmdOutput
    timeout = waits.expectedAgentConnected()
    looper.run(eventually(checkConnectedToEnv, poolCLI, retryWait=1,
                          timeout=timeout))
    poolCLI.enterCmd("status")
    assert "Connected to sandbox Indy network" == poolCLI.lastCmdOutput


def testCreateMultiPoolNodes(multiPoolNodesCreated):
    assert len(multiPoolNodesCreated) == 2


@pytest.fixture(scope="module")
def pool1(multiPoolNodesCreated):
    return multiPoolNodesCreated[0]


@pytest.fixture(scope="module")
def pool2(multiPoolNodesCreated):
    return multiPoolNodesCreated[1]


def test_connect_to_different_pools(do, be, cliForMultiNodePools):
    be(cliForMultiNodePools)
    do(None, expect=prompt_is("indy"))
    do('connect pool1', within=5, expect=["Connected to pool1"])
    do(None, expect=prompt_is("indy@pool1"))
    do('connect pool2', within=5, expect=["Connected to pool2"])
    do(None, expect=prompt_is("indy@pool2"))
    do('connect pool1', within=5, expect=["Connected to pool1"])
    do(None, expect=prompt_is("indy@pool1"))
