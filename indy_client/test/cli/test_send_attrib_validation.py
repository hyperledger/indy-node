import json
from base64 import b64encode
from binascii import hexlify
from hashlib import sha256

import pytest
from libnacl import randombytes
from libnacl.secret import SecretBox
from plenum.common.util import rawToFriendly, friendlyToRaw
from stp_core.crypto.util import randomSeed

from indy_client.test.cli.conftest import trusteeCli
from indy_client.test.cli.constants import ERROR, INVALID_SYNTAX
from indy_client.test.cli.helper import addNym, newKey, \
    createUuidIdentifier, createCryptonym, createHalfKeyIdentifierAndAbbrevVerkey

ATTRIBUTE_ADDED = 'Attribute added for nym {dest}'


@pytest.yield_fixture(scope='function')
def pureLocalCli(CliBuilder):
    yield from CliBuilder('Local')


@pytest.fixture(scope='function')
def localTrusteeCli(be, do, trusteeMap, poolNodesStarted,
                    nymAddedOut, pureLocalCli):
    return trusteeCli(be, do, trusteeMap, poolNodesStarted,
                      nymAddedOut, pureLocalCli)


def testSendAttribSucceedsForExistingUuidDest(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'name': 'Alice'
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribFailsForNotExistingUuidDest(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'name': 'Alice'
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribSucceedsForExistingDidDest(
        be, do, poolNodesStarted, localTrusteeCli):

    seed = randomSeed()
    idr, verkey = createHalfKeyIdentifierAndAbbrevVerkey(seed=seed)

    userCli = localTrusteeCli
    addNym(be, do, userCli, idr=idr, verkey=verkey)
    newKey(be, do, userCli, seed=seed.decode())

    sendAttribParameters = {
        'dest': idr,
        'raw': json.dumps({
            'name': 'Alice'
        })
    }

    be(userCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=sendAttribParameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribFailsForNotExistingCryptonymDest(
        be, do, poolNodesStarted, localTrusteeCli):

    seed = randomSeed()
    cryptonym = createCryptonym(seed=seed)

    userCli = localTrusteeCli
    newKey(be, do, userCli, seed=seed.decode())

    sendAttribParameters = {
        'dest': cryptonym,
        'raw': json.dumps({
            'name': 'Alice'
        })
    }

    be(userCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=sendAttribParameters, expect=ERROR, within=2)


def testSendAttribFailsIfDestIsPassedInHexFormat(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    hexEncodedUuidIdentifier = hexlify(friendlyToRaw(uuidIdentifier)).decode()

    parameters = {
        'dest': hexEncodedUuidIdentifier,
        'raw': json.dumps({
            'name': 'Alice'
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsIfDestIsInvalid(
        be, do, poolNodesStarted, trusteeCli):

    cryptonym = createCryptonym()
    invalidIdentifier = cryptonym[:-4]

    sendAttribParameters = {
        'dest': invalidIdentifier,
        'raw': json.dumps({
            'name': 'Alice'
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=sendAttribParameters, expect=ERROR, within=2)


def testSendAttribHasInvalidSyntaxIfDestIsEmpty(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'dest': '',
        'raw': json.dumps({
            'name': 'Alice'
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribHasInvalidSyntaxIfDestIsOmitted(
        be, do, poolNodesStarted, trusteeCli):

    parameters = {
        'raw': json.dumps({
            'name': 'Alice'
        })
    }

    be(trusteeCli)
    do('send ATTRIB raw={raw}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribSucceedsForRawWithOneAttr(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'name': 'Alice'
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribSucceedsForRawWithCompoundAttr(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'dateOfBirth': {
                'year': 1984,
                'month': 5,
                'dayOfMonth': 23
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribSucceedsForRawWithNullifiedAttr(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'name': None
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribSucceedsForRawWithEndpointWithHaContainingIpAddrAndPort(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': '52.11.117.186:6321'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribSucceedsForRawWithEndpointWithHaBeingNull(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': None
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribSucceedsForRawWithEndpointWithValidHaAndOtherProperties(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': '52.11.117.186:6321',
                'name': 'SOV Agent',
                'description': 'The SOV agent.'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribSucceedsForRawWithEndpointWithoutHaButWithOtherProperties(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'name': 'SOV Agent',
                'description': 'The SOV agent.'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribSucceedsForRawWithEndpointWithoutProperties(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {}
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribSucceedsForRawWithEndpointBeingNull(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': None
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribFailsForRawWithEndpointWithHaIfIpAddrHasWrongFormat(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': '52.11.117:6321'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaIfSomeIpComponentsAreNegative(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': '52.-1.117.186:6321'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaIfSomeIpCompHigherThanUpperBound(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': '52.11.256.186:6321'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaIfIpAddrIsEmpty(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': ':6321'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaIfPortIsNegative(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': '52.11.117.186:-1'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaIfPortIsHigherThanUpperBound(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': '52.11.117.186:65536'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaIfPortIsFloat(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': '52.11.117.186:6321.5'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaIfPortHasWrongFormat(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': '52.11.117.186:ninety'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaIfPortIsEmpty(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': '52.11.117.186:'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaContainingIpAddrOnly(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': '52.11.117.186'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaContainingPortOnly(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': '6321'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaContainingDomainNameAndPort(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': 'sovrin.org:6321'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaContainingDomainNameOnly(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': 'sovrin.org'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaBeingHumanReadableText(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': 'This is not a host address.'
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithHaBeingDecimalNumber(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': 42
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointWithEmptyHa(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': {
                'ha': ''
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForRawWithEndpointBeingEmptyString(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'endpoint': ''
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsIfRawContainsMulipleAttrs(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'name': 'Alice',
            'dateOfBirth': '05/23/2017'
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsIfRawContainsNoAttrs(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({})
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsIfRawIsBrokenJson(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    validJson = json.dumps({
        'name': 'Alice'
    })

    brokenJson = validJson[:-1]

    parameters = {
        'dest': uuidIdentifier,
        'raw': brokenJson
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)

    brokenJson = validJson.replace(':', '-')
    parameters['raw'] = brokenJson
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsIfRawIsHex(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': hexlify(randombytes(32)).decode()
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribFailsIfRawIsHumanReadableText(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': 'This is not a json.'
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribFailsIfRawIsDecimalNumber(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': 42
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribHasInvalidSyntaxIfRawIsEmptyString(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': ''
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribSucceedsForHexSha256Hash(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    raw = json.dumps({
        'name': 'Alice'
    })

    parameters = {
        'dest': uuidIdentifier,
        'hash': sha256(raw.encode()).hexdigest()
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} hash={hash}',
       mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribSucceedsForHexHashWithLettersInBothCases(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'hash': '6d4a333838d0ef96756cccC680AF2531075C512502Fb68c5503c63d93de859b3'
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} hash={hash}',
       mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribFailsForHashShorterThanSha256(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'hash': hexlify(randombytes(31)).decode()
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} hash={hash}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForHashLongerThanSha256(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'hash': hexlify(randombytes(33)).decode()
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} hash={hash}',
       mapper=parameters, expect=ERROR, within=2)


def testSendAttribFailsForBase58Hash(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    raw = json.dumps({
        'name': 'Alice'
    })

    hash = sha256(raw.encode()).digest()

    parameters = {
        'dest': uuidIdentifier,
        'hash': rawToFriendly(hash)
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} hash={hash}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribFailsForBase64Hash(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    raw = json.dumps({
        'name': 'Alice'
    })

    hash = sha256(raw.encode()).digest()

    parameters = {
        'dest': uuidIdentifier,
        'hash': b64encode(hash).decode()
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} hash={hash}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribHasInvalidSyntaxIfHashIsEmpty(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'hash': ''
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} hash={hash}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribSucceedsForNonEmptyEnc(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    raw = json.dumps({
        'name': 'Alice'
    })

    secretBox = SecretBox()

    parameters = {
        'dest': uuidIdentifier,
        'enc': secretBox.encrypt(raw.encode()).hex()
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} enc={enc}',
       mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)


def testSendAttribHasInvalidSyntaxIfEncIsEmpty(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'enc': ''
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} enc={enc}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribHasInvalidSyntaxIfRawAndHashPassedAtSameTime(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    raw = json.dumps({
        'name': 'Alice'
    })

    parameters = {
        'dest': uuidIdentifier,
        'raw': raw,
        'hash': sha256(raw.encode()).hexdigest()
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw} hash={hash}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribHasInvalidSyntaxIfRawAndEncPassedAtSameTime(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    raw = json.dumps({
        'name': 'Alice'
    })

    secretBox = SecretBox()

    parameters = {
        'dest': uuidIdentifier,
        'raw': raw,
        'enc': secretBox.encrypt(raw.encode()).hex()
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw} enc={enc}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribHasInvalidSyntaxIfHashAndEncPassedAtSameTime(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    raw = json.dumps({
        'name': 'Alice'
    })

    secretBox = SecretBox()
    encryptedRaw = secretBox.encrypt(raw.encode())

    parameters = {
        'dest': uuidIdentifier,
        'hash': sha256(encryptedRaw).hexdigest(),
        'enc': encryptedRaw.hex()
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} hash={hash} enc={enc}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribHasInvalidSyntaxIfRawHashAndEncPassedAtSameTime(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    raw = json.dumps({
        'name': 'Alice'
    })

    secretBox = SecretBox()
    encryptedRaw = secretBox.encrypt(raw.encode())

    parameters = {
        'dest': uuidIdentifier,
        'raw': raw,
        'hash': sha256(encryptedRaw).hexdigest(),
        'enc': encryptedRaw.hex()
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw} hash={hash} enc={enc}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribHasInvalidSyntaxIfUnknownParameterIsPassed(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'name': 'Alice'
        }),
        'extra': 42
    }

    be(trusteeCli)
    do('send ATTRIB dest={dest} raw={raw} extra={extra}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribHasInvalidSyntaxIfParametersOrderIsWrong(
        be, do, poolNodesStarted, trusteeCli):

    uuidIdentifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=uuidIdentifier)

    parameters = {
        'dest': uuidIdentifier,
        'raw': json.dumps({
            'name': 'Alice'
        })
    }

    be(trusteeCli)
    do('send ATTRIB raw={raw} dest={dest}',
       mapper=parameters, expect=INVALID_SYNTAX, within=2)


def testSendAttribHasInvalidSyntaxIfAllParametersAreOmitted(
        be, do, poolNodesStarted, trusteeCli):

    be(trusteeCli)
    do('send ATTRIB', expect=INVALID_SYNTAX, within=2)
