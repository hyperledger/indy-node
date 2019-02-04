import pytest
from plenum.common.constants import CURRENT_PROTOCOL_VERSION

from indy_common.req_utils import get_write_claim_def_signature_type, \
    get_write_claim_def_schema_ref, get_write_claim_def_tag, get_write_claim_def_public_keys, \
    get_read_claim_def_signature_type, get_read_claim_def_schema_ref, get_read_claim_def_tag, get_read_claim_def_from, \
    get_txn_claim_def_public_keys, get_txn_claim_def_tag, get_txn_claim_def_schema_ref, get_txn_claim_def_signature_type
from indy_common.types import SafeRequest
from plenum.common.txn_util import reqToTxn


@pytest.fixture()
def write_claim_def_request(request):
    req = {
        'operation': {
            'type': '102',
            'signature_type': 'CL1',
            'ref': 18,
            'tag': 'key111',
            'data': {
                'primary': {'primaryKey1': 'a'},
                'revocation': {'revocationKey1': 'b'}
            },
        },

        'identifier': 'L5AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514280215504647,
        'protocolVersion': CURRENT_PROTOCOL_VERSION,
        'signature': '5ZTp9g4SP6t73rH2s8zgmtqdXyTuSMWwkLvfV1FD6ddHCpwTY5SAsp8YmLWnTgDnPXfJue3vJBWjy89bSHvyMSdS'
    }
    return SafeRequest(**req)


@pytest.fixture()
def write_claim_def_request_no_signature_type(write_claim_def_request):
    del write_claim_def_request.operation['signature_type']
    return write_claim_def_request


@pytest.fixture()
def write_claim_def_request_no_tag(write_claim_def_request):
    del write_claim_def_request.operation['tag']
    return write_claim_def_request


@pytest.fixture(scope="module")
def read_claim_def_request():
    req = {
        'operation': {
            'type': '108',
            'signature_type': 'CL1',
            'ref': 18,
            'tag': 'key111',
            'origin': 'L5AD5g65TDQr1PPHHRoiGf'
        },

        'identifier': 'E5AD5g65TDQr1PPHHRoiGf',
        'reqId': 1514280215504647,
        'protocolVersion': CURRENT_PROTOCOL_VERSION
    }
    return SafeRequest(**req)


@pytest.fixture(scope="module")
def read_claim_def_request_no_signature_type(read_claim_def_request):
    del read_claim_def_request.operation['signature_type']
    return read_claim_def_request


@pytest.fixture(scope="module")
def read_claim_def_request_no_tag(read_claim_def_request):
    del read_claim_def_request.operation['tag']
    return read_claim_def_request


def test_get_write_claim_def_signature_type(write_claim_def_request):
    assert 'CL1' == get_write_claim_def_signature_type(write_claim_def_request)


def test_get_write_claim_def_signature_type_default(write_claim_def_request_no_signature_type):
    assert 'CL' == get_write_claim_def_signature_type(write_claim_def_request_no_signature_type)


def test_get_write_claim_def_schema_ref(write_claim_def_request):
    assert 18 == get_write_claim_def_schema_ref(write_claim_def_request)


def test_get_write_claim_def_tag(write_claim_def_request):
    assert 'key111' == get_write_claim_def_tag(write_claim_def_request)


def test_get_write_claim_def_tag_default(write_claim_def_request_no_tag):
    assert 'tag' == get_write_claim_def_tag(write_claim_def_request_no_tag)


def test_get_write_claim_public_keys(write_claim_def_request):
    assert {'primary': {'primaryKey1': 'a'}, 'revocation': {'revocationKey1': 'b'}} == \
        get_write_claim_def_public_keys(write_claim_def_request)


def test_get_txn_claim_def_signature_type(write_claim_def_request):
    txn = reqToTxn(write_claim_def_request)
    assert 'CL1' == get_txn_claim_def_signature_type(txn)


def test_get_txn_claim_def_signature_type_default(write_claim_def_request_no_signature_type):
    txn = reqToTxn(write_claim_def_request_no_signature_type)
    assert 'CL' == get_txn_claim_def_signature_type(txn)


def test_get_txn_claim_def_schema_ref(write_claim_def_request):
    txn = reqToTxn(write_claim_def_request)
    assert 18 == get_txn_claim_def_schema_ref(txn)


def test_get_txn_claim_def_tag(write_claim_def_request):
    txn = reqToTxn(write_claim_def_request)
    assert 'key111' == get_txn_claim_def_tag(txn)


def test_get_txn_claim_def_tag_default(write_claim_def_request_no_tag):
    txn = reqToTxn(write_claim_def_request_no_tag)
    assert 'tag' == get_txn_claim_def_tag(txn)


def test_get_txn_claim_public_keys(write_claim_def_request):
    txn = reqToTxn(write_claim_def_request)
    assert {'primary': {'primaryKey1': 'a'}, 'revocation': {'revocationKey1': 'b'}} == \
        get_txn_claim_def_public_keys(txn)


def test_get_read_claim_def_signature_type(read_claim_def_request):
    assert 'CL1' == get_read_claim_def_signature_type(read_claim_def_request)


def test_get_read_claim_def_signature_type_default(read_claim_def_request_no_signature_type):
    assert 'CL' == get_read_claim_def_signature_type(read_claim_def_request_no_signature_type)


def test_get_read_claim_def_schema_ref(read_claim_def_request):
    assert 18 == get_read_claim_def_schema_ref(read_claim_def_request)


def test_get_read_claim_def_tag(read_claim_def_request):
    assert 'key111' == get_read_claim_def_tag(read_claim_def_request)


def test_get_read_claim_def_tag_default(read_claim_def_request_no_tag):
    assert 'tag' == get_read_claim_def_tag(read_claim_def_request_no_tag)


def test_get_read_claim_def_from(read_claim_def_request):
    assert 'L5AD5g65TDQr1PPHHRoiGf' == get_read_claim_def_from(read_claim_def_request)
