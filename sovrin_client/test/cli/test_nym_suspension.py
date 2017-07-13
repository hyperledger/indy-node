from binascii import hexlify
from copy import copy

import pytest
from plenum.common.signer_did import DidSigner

from plenum.common.signer_simple import SimpleSigner
from sovrin_client.test.cli.conftest import nymAddedOut
from sovrin_common.roles import Roles


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
    do('send NYM dest={{remote}} role={role} verkey={{remote_verkey}}'.format(role=Roles.TRUST_ANCHOR.name),
       within=5,
       expect=nymAddedOut, mapper=v)
    return v


@pytest.yield_fixture(scope="module")
def trustAnchorCLI(CliBuilder):
    yield from CliBuilder("TrustAnchor")


@pytest.fixture(scope="module")
def trustAnchorCli(trustAnchorCLI, be, do, connectedToTest, trustAnchorAdded):
    be(trustAnchorCLI)
    do('new keyring TS', expect=['New keyring TS created',
                                   'Active keyring set to "TS"'])
    seed = hexlify(vals['newTrustAnchorIdr'][1]).decode()
    do('new key with seed {seed}', expect=['Key created in keyring TS'],
       mapper={'seed': seed})
    do('connect test', within=3, expect=connectedToTest)
    return trustAnchorCLI


@pytest.yield_fixture(scope="module")
def anotherTrusteeCLI(CliBuilder):
    yield from CliBuilder("NewTrustee")


@pytest.fixture(scope="module")
def anotherTrusteeCli(anotherTrusteeCLI, be, do, connectedToTest, anotherTrusteeAdded):
    be(anotherTrusteeCLI)
    do('new keyring TS1', expect=['New keyring TS1 created',
                                   'Active keyring set to "TS1"'])
    seed = hexlify(vals['newTrusteeIdr'][1]).decode()
    do('new key with seed {seed}', expect=['Key created in keyring TS1'],
       mapper={'seed': seed})
    do('connect test', within=3, expect=connectedToTest)
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
    errorMsg = 'InvalidClientRequest'
    do('send NYM dest={remote} role=',
       within=5,
       expect=[errorMsg], mapper=stewardAdded)


def testTrusteeSuspendingSteward(be, do, trusteeCli, stewardAdded, nymAddedOut):
    be(trusteeCli)
    do('send NYM dest={remote} role=',
       within=5,
       expect=nymAddedOut, mapper=stewardAdded)


def testTrusteeSuspendingTGB(be, do, trusteeCli, tbgAdded, nymAddedOut):
    be(trusteeCli)
    do('send NYM dest={remote} role=',
       within=5,
       expect=nymAddedOut, mapper=tbgAdded)

