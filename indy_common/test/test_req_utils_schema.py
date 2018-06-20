import pytest
from plenum.common.constants import CURRENT_PROTOCOL_VERSION

from indy_common.req_utils import get_write_schema_name, get_write_schema_version, get_write_schema_attr_names, \
    get_read_schema_version, get_read_schema_name, get_read_schema_from, get_txn_schema_name, get_txn_schema_version, \
    get_txn_schema_attr_names, get_reply_schema_version, get_reply_schema_name, get_reply_schema_from, \
    get_reply_schema_attr_names
from indy_common.types import SafeRequest
from plenum.common.txn_util import reqToTxn


@pytest.fixture(scope="module")
def write_schema_request(request):
    req = {
        'operation': {
            'type': '101',
            'data': {
                'version': '1.0',
                'name': 'Degree',
                'attr_names': ['undergrad', 'last_name', 'first_name', 'birth_date', 'postgrad', 'expiry_date']
            },
        },

        'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514280215504647,
        'protocolVersion': CURRENT_PROTOCOL_VERSION,
        'signature': '5ZTp9g4SP6t73rH2s8zgmtqdXyTuSMWwkLvfV1FD6ddHCpwTY5SAsp8YmLWnTgDnPXfJue3vJBWjy89bSHvyMSdS'
    }
    return SafeRequest(**req)


@pytest.fixture(scope="module")
def read_schema_request():
    req = {
        'operation': {
            'type': '107',
            'dest': 'L5AD5g65TDQr1PPHHRoiGf',
            'data': {
                'version': '1.0',
                'name': 'Degree',
            }
        },

        'identifier': 'E5AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514280215504647,
        'protocolVersion': CURRENT_PROTOCOL_VERSION
    }
    return SafeRequest(**req)


@pytest.fixture(scope="module")
def get_schema_reply():
    return {
        'type': '107',
        'dest': 'L5AD5g65TDQr1PPHHRoiGf',
        'data': {
            'version': '1.0',
            'name': 'Degree',
            'attr_names': ['undergrad', 'last_name', 'first_name', 'birth_date', 'postgrad', 'expiry_date']
        },

        'identifier': 'E5AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514280215504647,
        'protocolVersion': CURRENT_PROTOCOL_VERSION,

        'seqNo': 10,
        'txnTime': 1514214795,
    }


def test_get_write_schema_name(write_schema_request):
    assert 'Degree' == get_write_schema_name(write_schema_request)


def test_get_write_schema_version(write_schema_request):
    assert '1.0' == get_write_schema_version(write_schema_request)


def test_get_write_schema_attr_names(write_schema_request):
    assert ['undergrad', 'last_name', 'first_name', 'birth_date', 'postgrad',
            'expiry_date'] == get_write_schema_attr_names(write_schema_request)


def test_get_txn_schema_name(write_schema_request):
    txn = reqToTxn(write_schema_request)
    assert 'Degree' == get_txn_schema_name(txn)


def test_get_txn_schema_version(write_schema_request):
    txn = reqToTxn(write_schema_request)
    assert '1.0' == get_txn_schema_version(txn)


def test_get_txn_schema_attr_names(write_schema_request):
    txn = reqToTxn(write_schema_request)
    assert ['undergrad', 'last_name', 'first_name', 'birth_date', 'postgrad',
            'expiry_date'] == get_txn_schema_attr_names(txn)


def test_get_read_schema_name(read_schema_request):
    assert 'Degree' == get_read_schema_name(read_schema_request)


def test_get_read_schema_version(read_schema_request):
    assert '1.0' == get_read_schema_version(read_schema_request)


def test_get_read_schema_from(read_schema_request):
    assert 'L5AD5g65TDQr1PPHHRoiGf' == get_read_schema_from(read_schema_request)


def test_get_reply_schema_name(get_schema_reply):
    assert 'Degree' == get_reply_schema_name(get_schema_reply)


def test_get_reply_schema_version(get_schema_reply):
    assert '1.0' == get_reply_schema_version(get_schema_reply)


def test_get_reply_schema_from(get_schema_reply):
    assert 'L5AD5g65TDQr1PPHHRoiGf' == get_reply_schema_from(get_schema_reply)


def test_get_reply_schema_attr_names(get_schema_reply):
    assert ['undergrad', 'last_name', 'first_name', 'birth_date', 'postgrad',
            'expiry_date'] == get_reply_schema_attr_names(get_schema_reply)
