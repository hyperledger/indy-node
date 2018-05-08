import pytest
import json

from libnacl.secret import SecretBox
from hashlib import sha256

from indy_client.test.cli.constants import INVALID_SYNTAX
from indy_client.test.cli.helper import createUuidIdentifier, addNym


attrib_name = 'dateOfBirth'

secretBox = SecretBox()
enc_data = secretBox.encrypt(json.dumps({'name': 'Alice'}).encode()).hex()
hash_data = sha256(json.dumps({'name': 'Alice'}).encode()).hexdigest()

FOUND_ATTRIBUTE = 'Found attribute'
ATTRIBUTE_ADDED = 'Attribute added for nym {valid_dest}'
RETURNED_RAW_DATA = [FOUND_ATTRIBUTE, attrib_name, 'dayOfMonth', 'year', 'month']
RETURNED_ENC_DATA = [FOUND_ATTRIBUTE, enc_data]
RETURNED_HASH_DATA = [FOUND_ATTRIBUTE, hash_data]
ATTR_NOT_FOUND = 'Attr not found'


@pytest.fixture(scope="module")
def send_raw_attrib(be, do, poolNodesStarted, trusteeCli):

    valid_identifier = createUuidIdentifier()
    invalid_identifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=valid_identifier)

    parameters = {
        'attrib_name': attrib_name,
        'valid_dest': valid_identifier,
        'invalid_dest': invalid_identifier,
        'raw': json.dumps({
            attrib_name: {
                'dayOfMonth': 23,
                'year': 1984,
                'month': 5
            }
        })
    }

    be(trusteeCli)
    do('send ATTRIB dest={valid_dest} raw={raw}',
        mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)

    return parameters


@pytest.fixture(scope="module")
def send_enc_attrib(be, do, poolNodesStarted, trusteeCli):

    valid_identifier = createUuidIdentifier()
    invalid_identifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=valid_identifier)

    parameters = {
        'valid_dest': valid_identifier,
        'invalid_dest': invalid_identifier,
        'enc': enc_data
    }

    be(trusteeCli)
    do('send ATTRIB dest={valid_dest} enc={enc}',
        mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)

    return parameters


@pytest.fixture(scope="module")
def send_hash_attrib(be, do, poolNodesStarted, trusteeCli):

    valid_identifier = createUuidIdentifier()
    invalid_identifier = createUuidIdentifier()
    addNym(be, do, trusteeCli, idr=valid_identifier)

    parameters = {
        'valid_dest': valid_identifier,
        'invalid_dest': invalid_identifier,
        'hash': hash_data
    }

    be(trusteeCli)
    do('send ATTRIB dest={valid_dest} hash={hash}',
        mapper=parameters, expect=ATTRIBUTE_ADDED, within=2)

    return parameters


def test_send_get_attr_succeeds_for_existing_uuid_dest(
        be, do, poolNodesStarted, trusteeCli, send_raw_attrib):

    be(trusteeCli)
    do('send GET_ATTR dest={valid_dest} raw={attrib_name}',
       mapper=send_raw_attrib, expect=RETURNED_RAW_DATA, within=2)


def test_send_get_attr_fails_for_invalid_uuid_dest(
        be, do, poolNodesStarted, trusteeCli, send_raw_attrib):

    do('send GET_ATTR dest={invalid_dest} raw={attrib_name}',
       mapper=send_raw_attrib, expect=ATTR_NOT_FOUND, within=2)


def test_send_get_attr_fails_for_nonexistent_uuid_dest(
        be, do, poolNodesStarted, trusteeCli, send_raw_attrib):

    with pytest.raises(AssertionError) as excinfo:
        do('send GET_ATTR dest=this_is_not_valid raw={attrib_name}',
           mapper=send_raw_attrib, expect=ATTR_NOT_FOUND, within=2)
        assert(INVALID_SYNTAX in str(excinfo.value))


def test_send_get_attr_fails_for_invalid_attrib(
        be, do, poolNodesStarted, trusteeCli, send_raw_attrib):

    do('send GET_ATTR dest={valid_dest} raw=badname',
       mapper=send_raw_attrib, expect=ATTR_NOT_FOUND, within=2)


def test_send_get_attr_fails_with_missing_dest(
        be, do, poolNodesStarted, trusteeCli, send_raw_attrib):

    with pytest.raises(AssertionError) as excinfo:
        do('send GET_ATTR raw={attrib_name}',
            mapper=send_raw_attrib, expect=ATTR_NOT_FOUND, within=2)
    assert(INVALID_SYNTAX in str(excinfo.value))


def test_send_get_attr_fails_with_missing_attrib(
        be, do, poolNodesStarted, trusteeCli, send_raw_attrib):

    with pytest.raises(AssertionError) as excinfo:
        do('send GET_ATTR dest={valid_dest}',
            mapper=send_raw_attrib, expect=ATTR_NOT_FOUND, within=2)
    assert(INVALID_SYNTAX in str(excinfo.value))


def test_send_get_attr_enc_succeeds_for_existing_uuid_dest(
        be, do, poolNodesStarted, trusteeCli, send_enc_attrib):

    be(trusteeCli)
    do('send GET_ATTR dest={valid_dest} enc={enc}',
       mapper=send_enc_attrib, expect=RETURNED_ENC_DATA, within=2)


def test_send_get_attr_hash_succeeds_for_existing_uuid_dest(
        be, do, poolNodesStarted, trusteeCli, send_hash_attrib):

    be(trusteeCli)
    do('send GET_ATTR dest={valid_dest} hash={hash}',
       mapper=send_hash_attrib, expect=RETURNED_HASH_DATA, within=2)
