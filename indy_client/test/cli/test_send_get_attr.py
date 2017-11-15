import pytest
import json

from indy_client.test.cli.constants import INVALID_SYNTAX
from indy_client.test.cli.helper import createUuidIdentifier, addNym

attrib_name = 'dateOfBirth'

ATTRIBUTE_ADDED = 'Attribute added for nym {valid_dest}'
RETURNED_DATA = ['Found attribute', attrib_name, 'dayOfMonth', 'year', 'month']
ATTR_NOT_FOUND = 'Attr not found'


@pytest.fixture(scope="module")
def send_attrib(be, do, poolNodesStarted, trusteeCli):

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


def test_send_get_attr_succeeds_for_existing_uuid_dest(
        be, do, poolNodesStarted, trusteeCli, send_attrib):

    be(trusteeCli)
    do('send GET_ATTR dest={valid_dest} raw={attrib_name}',
       mapper=send_attrib, expect=RETURNED_DATA, within=2)


def test_send_get_attr_fails_for_invalid_uuid_dest(
        be, do, poolNodesStarted, trusteeCli, send_attrib):

    do('send GET_ATTR dest={invalid_dest} raw={attrib_name}',
       mapper=send_attrib, expect=ATTR_NOT_FOUND, within=2)


def test_send_get_attr_fails_for_nonexistent_uuid_dest(
        be, do, poolNodesStarted, trusteeCli, send_attrib):

    with pytest.raises(AssertionError) as excinfo:
        do('send GET_ATTR dest=this_is_not_valid raw={attrib_name}',
           mapper=send_attrib, expect=ATTR_NOT_FOUND, within=2)
        assert(INVALID_SYNTAX in str(excinfo.value))


def test_send_get_attr_fails_for_invalid_attrib(
        be, do, poolNodesStarted, trusteeCli, send_attrib):

    do('send GET_ATTR dest={valid_dest} raw=badname',
       mapper=send_attrib, expect=ATTR_NOT_FOUND, within=2)


def test_send_get_attr_fails_with_missing_dest(
        be, do, poolNodesStarted, trusteeCli, send_attrib):

    with pytest.raises(AssertionError) as excinfo:
        do('send GET_ATTR raw={attrib_name}',
            mapper=send_attrib, expect=ATTR_NOT_FOUND, within=2)
    assert(INVALID_SYNTAX in str(excinfo.value))


def test_send_get_attr_fails_with_missing_attrib(
        be, do, poolNodesStarted, trusteeCli, send_attrib):

    with pytest.raises(AssertionError) as excinfo:
        do('send GET_ATTR dest={valid_dest}',
            mapper=send_attrib, expect=ATTR_NOT_FOUND, within=2)
    assert(INVALID_SYNTAX in str(excinfo.value))
