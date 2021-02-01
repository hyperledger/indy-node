import pytest

from indy_common.authorize.helper import get_named_role
from plenum.common.constants import TRUSTEE_STRING, TRUSTEE


@pytest.mark.auth
def test_for_known_role():
    assert get_named_role(TRUSTEE) == TRUSTEE_STRING


@pytest.mark.auth
def test_for_unknown_role():
    assert get_named_role("SomeOtherRole") == "Unknown role"
