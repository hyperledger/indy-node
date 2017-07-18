import pytest

from sovrin_client.test.cli.test_tutorial import prompt_is
from stp_core.loop.eventually import eventually
from plenum.cli.cli import Exit


def testCliExitCommand(be, do, poolNodesStarted, aliceCLI, CliBuilder,
                       aliceMap, newKeyringOut, connectedToTest,
                       savedKeyringRestored, aliceKeyringMap):
    within = 3
    name = 'Alice'
    be(aliceCLI)
    do('prompt {}'.format(name), expect=prompt_is(name))
    do('new keyring {}'.format(name), expect=newKeyringOut, mapper=aliceMap)
    do('connect test', within=within, expect=connectedToTest)
    with pytest.raises(Exit):
        do('exit')

    def checkWalletRestore():
        # open cli again
        aliceCliNew = yield from CliBuilder(name)
        # check message of saved keyring alice restored
        be(aliceCliNew)
        do('connect test', within=within, expect=savedKeyringRestored,
           mapper=aliceKeyringMap)

    # check wallet restore
    aliceCLI.looper.run(eventually(checkWalletRestore, timeout=within))


@pytest.fixture(scope='module')
def aliceKeyringMap():
    return {
        'keyring-name': 'Alice'
    }
