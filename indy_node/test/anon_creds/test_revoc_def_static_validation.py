import copy
import json
import random

import pytest

from indy_common.constants import REVOC_TYPE, TAG, TAG_LIMIT_SIZE
from plenum.common.constants import GENERAL_LIMIT_SIZE, REQNACK, REJECT
from plenum.common.types import OPERATION
from plenum.common.util import randomString
from plenum.test.helper import sdk_sign_request_from_dict, sdk_send_signed_requests, sdk_get_replies



@pytest.fixture(scope="module", params=['lt', 'eq', 'gt'])
def _lt_eq_gt(request):
    return request.param


@pytest.fixture(scope="module", params=[REVOC_TYPE, TAG])
def _res_field_size(request, _lt_eq_gt):
    _field = request.param
    _expected = REQNACK if _lt_eq_gt == 'gt' else REJECT
    _valid_size = TAG_LIMIT_SIZE if _field == TAG else GENERAL_LIMIT_SIZE

    if _lt_eq_gt == 'lt':
        return _expected, _field, random.randint(1, _valid_size - 1)
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

    _req[OPERATION][_field] = randomString(_size)

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
