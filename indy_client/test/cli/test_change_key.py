import pytest
from indy_client.test.cli.helper import connect_and_check_output


def test_change_key(be, do, susanCLI, newStewardCli):
    # Generate new key in the wallet
    be(susanCLI)
    connect_and_check_output(do, susanCLI.txn_dir)
    do('new key', within=3, expect=["Key created in wallet"])

    # check that id cannot be used for the time
    id = susanCLI.activeDID
    verk = susanCLI.activeWallet.getVerkey(id)
    do('send NYM dest={}'.format(id), within=3, expect=[
       "Error: client request invalid: CouldNotAuthenticate("])

    # Add verkey
    be(newStewardCli)
    do('send NYM dest={} verkey={}'.format(id, verk),
       within=3, expect=["Nym {} added".format(id)])

    # check Susan's key is ok
    be(susanCLI)
    do('send NYM dest={}'.format(id), within=3,
       expect=["Nym {} added".format(id)])
    do('send GET_NYM dest={}'.format(id), within=3, expect=[
       "Current verkey for NYM {} is {}".format(id, verk)])

    # change key
    do('change current key', within=3, expect=["Adding nym {}".format(
        id), "Key changed for {}".format(id), "New verification key is"])

    # check new key
    assert id == susanCLI.activeDID
    assert verk != susanCLI.activeWallet.getVerkey(id)
    do('send NYM dest={}'.format(id), within=3,
       expect=["Nym {} added".format(id)])
    do('send GET_NYM dest={}'.format(id), within=3, expect=[
       "Current verkey for NYM {} is {}".format(id, susanCLI.activeWallet.getVerkey(id))])


def test_change_key_with_seed(be, do, philCli, newStewardCli):
    # Generate new key in the wallet
    be(philCli)
    connect_and_check_output(do, philCli.txn_dir)
    do('new key', within=3, expect=["Key created in wallet"])

    # check that id cannot be used for the time
    id = philCli.activeDID
    verk = philCli.activeWallet.getVerkey(id)
    do('send NYM dest={}'.format(id), within=3, expect=[
       "Error: client request invalid: CouldNotAuthenticate("])

    # Add verkey
    be(newStewardCli)
    do('send NYM dest={} verkey={}'.format(id, verk),
       within=3, expect=["Nym {} added".format(id)])

    # check Susan's key is ok
    be(philCli)
    do('send NYM dest={}'.format(id), within=3,
       expect=["Nym {} added".format(id)])
    do('send GET_NYM dest={}'.format(id), within=3, expect=[
       "Current verkey for NYM {} is {}".format(id, verk)])

    # change key
    seed = "8" * 32
    do('change current key with seed {}'.format(seed),
       within=3,
       expect=["Adding nym {}".format(id),
               "Key changed for {}".format(id),
               "New verification key is"])

    # check new key
    assert id == philCli.activeDID
    assert verk != philCli.activeWallet.getVerkey(id)
    do('send NYM dest={}'.format(id), within=3,
       expect=["Nym {} added".format(id)])
    do('send GET_NYM dest={}'.format(id), within=3, expect=[
       "Current verkey for NYM {} is {}".format(id, philCli.activeWallet.getVerkey(id))])
