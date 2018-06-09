import pytest

from indy_common.req_utils import get_write_schema_name, get_write_schema_version, get_write_schema_attr_names, \
    get_read_schema_version, get_read_schema_name, get_read_schema_from
from indy_common.types import SafeRequest


@pytest.fixture(scope="module", params=['dict', 'Request'])
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
        'protocolVersion': 1,
        'signature': '5ZTp9g4SP6t73rH2s8zgmtqdXyTuSMWwkLvfV1FD6ddHCpwTY5SAsp8YmLWnTgDnPXfJue3vJBWjy89bSHvyMSdS'
    }
    if request.param == 'dict':
        return req
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
        'protocolVersion': 1
    }
    return SafeRequest(**req)


def test_get_write_schema_name(write_schema_request):
    assert 'Degree' == get_write_schema_name(write_schema_request)


def test_get_write_schema_version(write_schema_request):
    assert '1.0' == get_write_schema_version(write_schema_request)


def test_get_write_schema_attr_names(write_schema_request):
    assert ['undergrad', 'last_name', 'first_name', 'birth_date', 'postgrad',
            'expiry_date'] == get_write_schema_attr_names(write_schema_request)


def test_get_read_schema_name(read_schema_request):
    assert 'Degree' == get_read_schema_name(read_schema_request)


def test_get_read_schema_version(read_schema_request):
    assert '1.0' == get_read_schema_version(read_schema_request)


def test_get_read_schema_from(read_schema_request):
    assert 'L5AD5g65TDQr1PPHHRoiGf' == get_read_schema_from(read_schema_request)
