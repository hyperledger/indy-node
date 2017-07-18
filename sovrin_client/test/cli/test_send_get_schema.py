import pytest
from sovrin_client.test.cli.constants import INVALID_SYNTAX
from sovrin_client.test.cli.helper import createUuidIdentifier
from sovrin_node.test.did.conftest import wallet


SCHEMA_ADDED = ['The following schema is published to the Sovrin distributed ledger', 'Sequence number is']
SCHEMA_FOUND = ['Found schema', 'Degree', '1.0','attrib1', 'attrib2', 'attrib3']
SCHEMA_NOT_FOUND = 'Schema not found'

@pytest.fixture(scope="module")
def aliceCli(be, do, poolNodesStarted, aliceCLI, connectedToTest, wallet):
    keyseed = 'a' * 32

    be(aliceCLI)
    addAndActivateCLIWallet(aliceCLI, wallet)
    do('connect test', within=3, expect=connectedToTest)
    do('new key with seed {}'.format(keyseed))

    return aliceCLI


def addAndActivateCLIWallet(cli, wallet):
    cli.wallets[wallet.name] = wallet
    cli.activeWallet = wallet


@pytest.fixture(scope="module")
def send_schema(be, do, poolNodesStarted, trusteeCli):

    be(trusteeCli)
    do('send SCHEMA name=Degree version=1.0 keys=attrib1,attrib2,attrib3',
       expect=SCHEMA_ADDED, within=5)


def test_send_get_schema_succeeds(be, do, poolNodesStarted, trusteeCli, send_schema):

    do('send GET_SCHEMA dest={} name=Degree version=1.0'.format(trusteeCli.activeIdentifier),
            expect=SCHEMA_FOUND, within=5)


def test_send_get_schema_as_alice(be, do, poolNodesStarted, trusteeCli, send_schema, aliceCli):

    be(aliceCli)
    do('send GET_SCHEMA dest={} name=Degree version=1.0'.format(trusteeCli.activeIdentifier),
            expect=SCHEMA_FOUND, within=5)


def test_send_get_schema_fails_with_invalid_name(
        be, do, poolNodesStarted, trusteeCli, send_schema):

    do('send GET_SCHEMA dest={} name=invalid version=1.0'.format(trusteeCli.activeIdentifier),
            expect=SCHEMA_NOT_FOUND, within=5)

def test_send_get_schema_fails_with_invalid_dest(
        be, do, poolNodesStarted, trusteeCli, send_schema):

    uuid_identifier = createUuidIdentifier()
    do('send GET_SCHEMA dest={} name=invalid version=1.0'.format(uuid_identifier),
            expect=SCHEMA_NOT_FOUND, within=5)

def test_send_get_schema_fails_with_invalid_version(
        be, do, poolNodesStarted, trusteeCli, send_schema):
    do('send GET_SCHEMA dest={} name=Degree version=2.0'.format(trusteeCli.activeIdentifier),
            expect=SCHEMA_NOT_FOUND, within=5)

def test_send_get_schema_fails_with_invalid_version_syntax(
        be, do, poolNodesStarted, trusteeCli, send_schema):

    with pytest.raises(AssertionError) as excinfo:
        do('send GET_SCHEMA dest={} name=Degree version=asdf'.format(trusteeCli.activeIdentifier),
            expect=SCHEMA_NOT_FOUND, within=5)
    assert(INVALID_SYNTAX in str(excinfo.value))

def test_send_get_schema_fails_without_version(
        be, do, poolNodesStarted, trusteeCli, send_schema):

    with pytest.raises(AssertionError) as excinfo:
        do('send GET_SCHEMA dest={} name=Degree'.format(trusteeCli.activeIdentifier),
            expect=SCHEMA_NOT_FOUND, within=5)
    assert(INVALID_SYNTAX in str(excinfo.value))

def test_send_get_schema_fails_without_name(
        be, do, poolNodesStarted, trusteeCli, send_schema):

    with pytest.raises(AssertionError) as excinfo:
        do('send GET_SCHEMA dest={} version=1.0'.format(trusteeCli.activeIdentifier),
            expect=SCHEMA_NOT_FOUND, within=5)
    assert(INVALID_SYNTAX in str(excinfo.value))

def test_send_get_schema_fails_without_dest(
        be, do, poolNodesStarted, trusteeCli, send_schema):

    with pytest.raises(AssertionError) as excinfo:
        do('send GET_SCHEMA name=Degree version=1.0',
            expect=SCHEMA_NOT_FOUND, within=5)
    assert(INVALID_SYNTAX in str(excinfo.value))