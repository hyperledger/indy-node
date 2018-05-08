import pytest
from indy_client.test.cli.helper import connect_and_check_output
from indy_node.test.did.conftest import wallet
from indy_client.test.cli.constants import INVALID_SYNTAX, SCHEMA_ADDED, \
    CLAIM_DEF_ADDED

CLAIM_DEF_FOUND = ['Found claim def', 'attrib1', 'attrib2', 'attrib3']
CLAIM_DEF_NOT_FOUND = 'Claim def not found'


@pytest.fixture(scope="module")
def create_schema_and_claim_def(be, do, poolNodesStarted, trusteeCli):

    be(trusteeCli)
    do('send SCHEMA name=Degree version=1.0 keys=attrib1,attrib2,attrib3',
       expect=SCHEMA_ADDED, within=5)

    RefNo = 0
    for s in trusteeCli.lastPrintArgs['msg'].split():
        if s.isdigit():
            RefNo = int(s)

    assert(RefNo > 0)

    # genKeys can take a random amount of time (genPrime)
    do('send CLAIM_DEF ref={} signature_type=CL'.format(RefNo),
       expect=CLAIM_DEF_ADDED, within=239)

    return RefNo


@pytest.fixture(scope="module")
def aliceCli(be, do, poolNodesStarted, aliceCLI, wallet):
    keyseed = 'a' * 32

    be(aliceCLI)
    addAndActivateCLIWallet(aliceCLI, wallet)
    connect_and_check_output(do, aliceCLI.txn_dir)
    do('new key with seed {}'.format(keyseed))

    return aliceCLI


def addAndActivateCLIWallet(cli, wallet):
    cli.wallets[wallet.name] = wallet
    cli.activeWallet = wallet


def test_send_get_claim_def_succeeds(be, do, poolNodesStarted,
                                     trusteeCli, create_schema_and_claim_def):

    be(trusteeCli)
    RefNo = create_schema_and_claim_def
    do('send GET_CLAIM_DEF ref={} signature_type=CL'.format(RefNo),
       expect=CLAIM_DEF_FOUND, within=5)


def test_send_get_claim_def_as_alice_fails(
        be,
        do,
        poolNodesStarted,
        trusteeCli,
        create_schema_and_claim_def,
        aliceCli):

    be(aliceCli)
    RefNo = create_schema_and_claim_def
    do('send GET_CLAIM_DEF ref={} signature_type=CL'.format(RefNo),
       expect=CLAIM_DEF_NOT_FOUND, within=5)


def test_send_get_claim_def_with_invalid_ref_fails(be, do, poolNodesStarted,
                                                   trusteeCli):

    be(trusteeCli)
    do('send GET_CLAIM_DEF ref=500 signature_type=CL',
       expect=CLAIM_DEF_NOT_FOUND, within=5)


def test_send_get_claim_def_with_invalid_signature_fails(
        be, do, poolNodesStarted, trusteeCli, create_schema_and_claim_def):

    be(trusteeCli)
    RefNo = create_schema_and_claim_def
    with pytest.raises(AssertionError) as excinfo:
        do('send GET_CLAIM_DEF ref={} signature_type=garbage'.format(RefNo),
            expect=CLAIM_DEF_NOT_FOUND, within=5)
    assert(INVALID_SYNTAX in str(excinfo.value))
