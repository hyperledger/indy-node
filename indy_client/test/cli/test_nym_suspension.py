from binascii import hexlify
from copy import copy

import pytest
from plenum.common.signer_did import DidSigner

from plenum.common.signer_simple import SimpleSigner
from indy_client.test.cli.helper import connect_and_check_output
from indy_client.test.cli.conftest import nymAddedOut
from indy_common.roles import Roles


def id_and_seed():
    s = DidSigner()
    return s.identifier, s.seed


vals = {
    'newTrusteeIdr': id_and_seed(),
    'newTGBIdr': id_and_seed(),
    'newStewardIdr': id_and_seed(),
    'newTrustAnchorIdr': id_and_seed(),
}


@pytest.fixture(scope="module")
def anotherTrusteeAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    v = copy(vals)
    v['remote'] = vals['newTrusteeIdr'][0]
    be(trusteeCli)
    do('send NYM dest={{remote}} role={role}'.format(role=Roles.TRUSTEE.name),
       within=5,
       expect=nymAddedOut, mapper=v)
    return v


@pytest.fixture(scope="module")
def tbgAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    v = copy(vals)
    v['remote'] = vals['newTGBIdr'][0]
    be(trusteeCli)
    do('send NYM dest={{remote}} role={role}'.format(role=Roles.TGB.name),
       within=5,
       expect=nymAddedOut, mapper=v)
    return v


@pytest.fixture(scope="module")
def stewardAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    v = copy(vals)
    v['remote'] = vals['newStewardIdr'][0]
    be(trusteeCli)
    do('send NYM dest={{remote}} role={role}'.format(role=Roles.STEWARD.name),
       within=5,
       expect=nymAddedOut, mapper=v)
    return v


@pytest.fixture(scope="module")
def trustAnchorAdded(be, do, trusteeCli, nymAddedOut):
    global vals
    v = copy(vals)
    v['remote'] = vals['newTrustAnchorIdr'][0]
    v['remote_verkey'] = DidSigner(seed=vals['newTrustAnchorIdr'][1]).verkey
    be(trusteeCli)
    do('send NYM dest={{remote}} role={role} verkey={{remote_verkey}}'.format(
        role=Roles.TRUST_ANCHOR.name), within=5, expect=nymAddedOut, mapper=v)
    return v


@pytest.yield_fixture(scope="module")
def trustAnchorCLI(CliBuilder):
    yield from CliBuilder("TrustAnchor")


@pytest.fixture(scope="module")
def trustAnchorCli(trustAnchorCLI, be, do, trustAnchorAdded):
    be(trustAnchorCLI)
    do('new wallet TS', expect=['New wallet TS created',
                                'Active wallet set to "TS"'])
    seed = hexlify(vals['newTrustAnchorIdr'][1]).decode()
    do('new key with seed {seed}', expect=['Key created in wallet TS'],
       mapper={'seed': seed})
    connect_and_check_output(do, trustAnchorCLI.txn_dir)
    return trustAnchorCLI


@pytest.yield_fixture(scope="module")
def anotherTrusteeCLI(CliBuilder):
    yield from CliBuilder("NewTrustee")


@pytest.fixture(scope="module")
def anotherTrusteeCli(anotherTrusteeCLI, be, do,
                      anotherTrusteeAdded):
    be(anotherTrusteeCLI)
    do('new wallet TS1', expect=['New wallet TS1 created',
                                 'Active wallet set to "TS1"'])
    seed = hexlify(vals['newTrusteeIdr'][1]).decode()
    do('new key with seed {seed}', expect=['Key created in wallet TS1'],
       mapper={'seed': seed})
    connect_and_check_output(do, anotherTrusteeCLI.txn_dir)
    return anotherTrusteeCLI


def testTrusteeSuspendingTrustAnchor(be, do, trusteeCli, trustAnchorAdded,
                                     nymAddedOut, trustAnchorCli):
    be(trusteeCli)
    do('send NYM dest={remote} role=',
       within=5,
       expect=nymAddedOut, mapper=trustAnchorAdded)
    s = DidSigner().identifier
    be(trustAnchorCli)
    errorMsg = "UnauthorizedClientRequest('None role cannot add None role'"
    do('send NYM dest={remote}',
       within=5,
       expect=[errorMsg], mapper={'remote': s})


def testTrusteeSuspendingTrustee(be, do, trusteeCli, anotherTrusteeAdded,
                                 nymAddedOut, anotherTrusteeCli, stewardAdded):
    be(trusteeCli)
    do('send NYM dest={remote} role=',
       within=5,
       expect=nymAddedOut, mapper=anotherTrusteeAdded)
    be(anotherTrusteeCli)
    errorMsg = 'CouldNotAuthenticate'
    do('send NYM dest={remote} role=',
       within=5,
       expect=[errorMsg], mapper=stewardAdded)


def testTrusteeSuspendingSteward(
        be, do, trusteeCli, stewardAdded, nymAddedOut):
    be(trusteeCli)
    do('send NYM dest={remote} role=',
       within=5,
       expect=nymAddedOut, mapper=stewardAdded)


def testTrusteeSuspendingTGB(be, do, trusteeCli, tbgAdded, nymAddedOut):
    be(trusteeCli)
    do('send NYM dest={remote} role=',
       within=5,
       expect=nymAddedOut, mapper=tbgAdded)


def testTrustAnchorSuspendingHimselfByVerkeyFlush(be, do, trusteeCli, trustAnchorAdded,
                                                  nymAddedOut, trustAnchorCli):
    # The trust anchor has already lost its role due to previous tests,
    # but it is ok for this test where the trust anchor flushes its verkey
    # and then he is unable to send NYM due to empty verkey.
    be(trustAnchorCli)
    do('send NYM dest={remote} verkey=',
       within=5,
       expect=nymAddedOut, mapper=trustAnchorAdded)

    s = DidSigner().identifier
    errorMsg = "CouldNotAuthenticate('Can not find verkey for"
    do('send NYM dest={remote}',
       within=5,
       expect=[errorMsg], mapper={'remote': s})
