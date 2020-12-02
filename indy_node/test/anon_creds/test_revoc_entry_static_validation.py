import copy
import json
import random

import pytest

from indy_common.constants import REVOC_TYPE, ACCUM, PREV_ACCUM, REVOC_REG_DEF_ID, REVOC_REG_ENTRY, VALUE, ISSUED, \
    REVOKED
from plenum.common.constants import REQNACK, REJECT, TXN_TYPE, GENERAL_LIMIT_SIZE
from plenum.common.util import randomString
from plenum.test.helper import sdk_send_signed_requests, sdk_get_replies, sdk_sign_request_from_dict


@pytest.fixture(scope="module", params=['lt', 'eq', 'gt'])
def _lt_eq_gt(request):
    return request.param


@pytest.fixture(scope="module")
def _entry_skeleton():
    return {
        REVOC_REG_DEF_ID: randomString(10),
        TXN_TYPE: REVOC_REG_ENTRY,
        REVOC_TYPE: randomString(10),
        VALUE: {
            PREV_ACCUM: randomString(10),
            ACCUM: randomString(10),
            ISSUED: [],
            REVOKED: [],
        }
    }


@pytest.fixture(scope="module", params=[REVOC_TYPE])
def _res_field_size(request, _lt_eq_gt):
    _field = request.param
    _expected = REQNACK if _lt_eq_gt == 'gt' else REJECT
    _valid_size = GENERAL_LIMIT_SIZE

    if _lt_eq_gt == 'lt':
        return _expected, _field, random.randint(0, _valid_size - 1)
    if _lt_eq_gt == 'eq':
        return _expected, _field, _valid_size
    return _expected, _field, random.randint(_valid_size + 1, 2 * _valid_size)


@pytest.fixture(scope="module")
def revoc_entry(looper,
                sdk_wallet_steward,
                _entry_skeleton,
                _lt_eq_gt,
                _res_field_size):
    _expected, _field, _size = _res_field_size
    _req = copy.deepcopy(_entry_skeleton)
    _value = randomString(_size)

    _req[_field] = _value

    return _expected, sdk_sign_request_from_dict(looper, sdk_wallet_steward, _req)


def test_revoc_entry_static_validation_on_size(revoc_entry,
                                               looper,
                                               txnPoolNodeSet,
                                               sdk_pool_handle,
                                               sdk_wallet_steward):
    _expected, _req = revoc_entry
    results = sdk_send_signed_requests(sdk_pool_handle, [json.dumps(_req)])
    _reply = sdk_get_replies(looper, results)[0][1]
    assert _expected == _reply['op']
