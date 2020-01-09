import copy
import json
import random

import pytest

from indy_common.constants import REVOC_TYPE, ID, CRED_DEF_ID, TAG, TAG_LIMIT_SIZE, TAILS_HASH, TAILS_LOCATION, VALUE
from plenum.common.constants import GENERAL_LIMIT_SIZE, REQNACK, REJECT
from plenum.common.types import OPERATION
from plenum.common.util import randomString
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_signed_requests, sdk_get_replies



@pytest.fixture(scope="module", params=['lt', 'eq', 'gt'])
def _lt_eq_gt(request):
    return request.param


@pytest.fixture(scope="module", params=[ID, REVOC_TYPE, TAG, CRED_DEF_ID, TAILS_HASH, TAILS_LOCATION])
def _res_field_size(request, _lt_eq_gt):
    _field = request.param
    _expected = REQNACK if _lt_eq_gt == 'gt' else REJECT
    _valid_size = TAG_LIMIT_SIZE if _field == TAG else GENERAL_LIMIT_SIZE

    if _lt_eq_gt == 'lt':
        return _expected, _field, random.randint(0, _valid_size - 1)
    if _lt_eq_gt == 'eq':
        return _expected, _field, _valid_size
    return _expected, _field, random.randint(_valid_size + 1, 2 * _valid_size)


@pytest.fixture(scope="module")
def revoc_def_req(looper,
                  sdk_wallet_steward,
                  build_revoc_def_by_default,
                  _res_field_size):
    _expected, _field, _size = _res_field_size
    _req = copy.deepcopy(build_revoc_def_by_default)
    _specific_value = ''

    if _field == CRED_DEF_ID:
        _orig_value = _req[OPERATION][CRED_DEF_ID]
        _specific_value = _orig_value + randomString(_size - len(_orig_value))

    if _field in (TAILS_HASH, TAILS_LOCATION):
        _req[OPERATION][VALUE][_field] = randomString(_size)
    else:
        _req[OPERATION][_field] = _specific_value if _specific_value else randomString(_size)

    return _expected, sdk_sign_request_from_dict(looper, sdk_wallet_steward, _req['operation'])


def test_revoc_def_static_validation_on_field_size(revoc_def_req,
                                                   looper,
                                                   txnPoolNodeSet,
                                                   sdk_pool_handle,
                                                   sdk_wallet_steward):
    _expected, _req = revoc_def_req
    results = sdk_send_signed_requests(sdk_pool_handle, [json.dumps(_req)])
    _reply = sdk_get_replies(looper, results)[0][1]
    assert _expected == _reply['op']
