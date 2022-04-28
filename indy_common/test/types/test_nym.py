from plenum.common.constants import TARGET_NYM, TXN_TYPE
import pytest
from indy_common.constants import DIDDOC_CONTENT, NYM
from indy_common.types import ClientNYMOperation

VALID_TARGET_NYM = 'a' * 43


@pytest.fixture
def validator():
    yield ClientNYMOperation()


def test_nym(validator):
    """Validate that the NYM transaction accepts only JSON
    strings as DIDDOC_CONTENT."""

    msg = {
        TXN_TYPE: NYM,
        TARGET_NYM: VALID_TARGET_NYM,
        DIDDOC_CONTENT: '{}',
    }
    validator.validate(msg)


def test_nym_raw_dictionary(validator):
    """Validate that the NYM transaction does not accept
    dictionaries as DIDDOC_CONTENT."""
    msg = {
        TXN_TYPE: NYM,
        TARGET_NYM: VALID_TARGET_NYM,
        DIDDOC_CONTENT: {},
    }
    with pytest.raises(TypeError) as ex_info:
        validator.validate(msg)

    ex_info.match("validation error")
