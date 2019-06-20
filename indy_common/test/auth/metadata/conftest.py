from itertools import combinations, product

import pytest

from indy_common.authorize.auth_constraints import IDENTITY_OWNER
from indy_common.constants import ENDORSER
from indy_common.test.auth.metadata.helper import PluginAuthorizer
from plenum.common.constants import TRUSTEE, STEWARD
from plenum.test.conftest import getValueFromModule

ROLES = [TRUSTEE, STEWARD, ENDORSER, IDENTITY_OWNER]
MAX_SIG_COUNT = 3


@pytest.fixture(scope='module')
def write_auth_req_validator(write_auth_req_validator):
    plugin_authorizer = PluginAuthorizer()
    write_auth_req_validator.register_authorizer(plugin_authorizer)
    return write_auth_req_validator


@pytest.fixture(scope='module', params=[None, 0, 1, 2, 3, 4, 100])
def amount(request):
    return request.param


@pytest.fixture(scope='module', params=[True, False])
def is_owner(request):
    return request.param


@pytest.fixture(
    scope='module',
    params=[role for r in range(len(ROLES) + 1) for role in combinations(ROLES, r)],
    ids=[str(role) for r in range(len(ROLES) + 1) for role in combinations(ROLES, r)]
)
def roles(request):
    '''
    Combination of all roles.

    Example:
      - roles=[A, B, C]
      ==> [(A), (B), (C), (A, B), (A, C), (B, C), (A, B, C)]
    '''
    return request.param


@pytest.fixture(scope='module')
def signatures(request, roles):
    '''
    Combinations of all signature types and signature count.

    Example:
          - roles=[A, B]
          - sig_count=1..3
          =>[(), (A: 1), (B:1), (A: 2), (B: 2), (A: 3), (B: 3),
             (A:1, B: 1), (A:2, B: 1), (A:1, B: 2), (A:2, B: 2),
             (A:1, B: 3), (A:3, B: 1), (A:3, B: 3),
             (A:2, B: 3), (A:3, B: 2)]

    '''
    max_sig_count = getValueFromModule(request, "MAX_SIG_COUNT", 3)
    all_sigs_count = list(range(1, max_sig_count))
    return [
        {role: sig_count for role, sig_count in zip(roles, sigs_count)}
        for sigs_count in product(all_sigs_count, repeat=len(roles))
    ]
