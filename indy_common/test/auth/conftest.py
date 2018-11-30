import pytest

from indy_common.auth import Authoriser, generate_auth_map
from plenum.common.constants import STEWARD, TRUSTEE

from indy_common.constants import TRUST_ANCHOR


@pytest.fixture(scope='function', params=[STEWARD, TRUSTEE, TRUST_ANCHOR, None])
def role(request):
    return request.param


@pytest.fixture(scope='function', params=[True, False])
def is_owner(request):
    return request.param


@pytest.fixture(scope='function', params=[None, "value1"])
def old_values(request):
    return request.param


@pytest.fixture(scope='module')
def initialized_auth_map():
    Authoriser.auth_map = generate_auth_map(Authoriser.ValidRoles, False)
