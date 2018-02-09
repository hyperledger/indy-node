from binascii import hexlify

import pytest
from plenum.common.util import friendlyToRaw

from indy_client.test.cli.constants import INVALID_SYNTAX
from indy_client.test.cli.helper import createUuidIdentifier, addNym, \
    createHalfKeyIdentifierAndAbbrevVerkey, createCryptonym
from indy_common.roles import Roles
from indy_node.test.helper import check_str_is_base58_compatible

CURRENT_VERKEY_FOR_NYM = 'Current verkey for NYM {dest} is {verkey}'
CURRENT_VERKEY_FOR_NYM_WITH_ROLE = 'Current verkey for NYM {dest} is ' \
                                   '{verkey} with role {role}'
CURRENT_VERKEY_IS_SAME_AS_IDENTIFIER = \
    'Current verkey is same as identifier {dest}'
NYM_NOT_FOUND = 'NYM {dest} not found'


def testSendGetNymSucceedsForExistingUuidDest(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    addNym(be, do, trusteeCli, idr=uuidIdentifier, verkey=abbrevVerkey)

    parameters = {
        'dest': uuidIdentifier,
        'verkey': abbrevVerkey
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest}',
       mapper=parameters, expect=CURRENT_VERKEY_FOR_NYM, within=2)


def testSendGetNymFailsForNotExistingUuidDest(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': createUuidIdentifier()
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest}',
       mapper=parameters, expect=NYM_NOT_FOUND, within=2)


def test_get_nym_returns_role(
        be, do, poolNodesStarted, trusteeCli):
    current_role = Roles.TRUST_ANCHOR
    uuidIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    addNym(be, do, trusteeCli, idr=uuidIdentifier, verkey=abbrevVerkey,
           role=current_role)

    parameters = {
        'dest': uuidIdentifier,
        'verkey': abbrevVerkey,
        'role': current_role
    }

    do('send GET_NYM dest={dest}',
       mapper=parameters, expect=CURRENT_VERKEY_FOR_NYM_WITH_ROLE, within=2)
    new_role = ''
    addNym(be, do, trusteeCli, idr=uuidIdentifier, verkey=abbrevVerkey,
           role=new_role)
    do('send GET_NYM dest={dest}',
       mapper=parameters, expect=CURRENT_VERKEY_FOR_NYM, within=2)


def testSendGetNymFailsIfCryptonymIsPassedAsDest(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': createCryptonym()
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest}',
       mapper=parameters, expect=NYM_NOT_FOUND, within=2)


def testSendGetNymFailsIfDestIsPassedInHexFormat(
        be, do, poolNodesStarted, trusteeCli):

    # Sometimes hex representation can use only base58 compatible characters
    while True:
        uuidIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
        hexEncodedUuidIdentifier = hexlify(
            friendlyToRaw(uuidIdentifier)).decode()
        if not check_str_is_base58_compatible(hexEncodedUuidIdentifier):
            break

    addNym(be, do, trusteeCli, idr=uuidIdentifier, verkey=abbrevVerkey)

    parameters = {
        'dest': hexEncodedUuidIdentifier
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest}',
       mapper=parameters,
       expect="should not contain the following chars",
       within=2)


def testSendGetNymFailsIfDestIsInvalid(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    invalidIdentifier = uuidIdentifier[:-4]

    parameters = {
        'dest': invalidIdentifier
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest}',
       mapper=parameters, expect="b58 decoded value length", within=2)


def testSendGetNymHasInvalidSyntaxIfDestIsEmpty(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': ''
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendGetNymHasInvalidSyntaxIfDestIsOmitted(
        be, do, poolNodesStarted, trusteeCli):

    be(trusteeCli)
    do('send GET_NYM', expect=INVALID_SYNTAX, within=2)


def testSendGetNymHasInvalidSyntaxIfUnknownParameterIsPassed(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier, abbrevVerkey = createHalfKeyIdentifierAndAbbrevVerkey()
    addNym(be, do, trusteeCli, idr=uuidIdentifier, verkey=abbrevVerkey)

    parameters = {
        'dest': uuidIdentifier,
        'extra': 42
    }

    be(trusteeCli)
    do('send GET_NYM dest={dest} extra={extra}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)
