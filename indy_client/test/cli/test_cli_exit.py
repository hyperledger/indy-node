import pytest

from indy_client.test.cli.helper import connect_and_check_output
from indy_client.test.cli.test_tutorial import prompt_is
from stp_core.loop.eventually import eventually
from plenum.cli.cli import Exit


def testCliExitCommand(be, do, poolNodesStarted, aliceCLI, CliBuilder,
                       aliceMap, newKeyringOut,
                       savedKeyringRestored, aliceKeyringMap):
    within = 3
    name = 'Alice'
    be(aliceCLI)
    do('prompt {}'.format(name), expect=prompt_is(name))
    do('new wallet {}'.format(name), expect=newKeyringOut, mapper=aliceMap)
    connect_and_check_output(do, aliceCLI.txn_dir)
    with pytest.raises(Exit):
        do('exit')

    def checkWalletRestore():
        # open cli again
        aliceCliNew = yield from CliBuilder(name)
        # check message of saved wallet alice restored
        be(aliceCliNew)
        connect_and_check_output(do, aliceCliNew.txn_dir, expect=savedKeyringRestored, mapper=aliceKeyringMap)

    # check wallet restore
    aliceCLI.looper.run(eventually(checkWalletRestore, timeout=within))


@pytest.fixture(scope='module')
def aliceKeyringMap():
    return {
        'wallet-name': 'Alice'
    }
