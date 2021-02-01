from collections import OrderedDict

import pytest

from indy_common.types import ClientClaimDefGetOperation
from plenum.common.messages.fields import ConstantField, LimitedLengthStringField, TxnSeqNoField, IdentifierField

EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("ref", TxnSeqNoField),
    ("origin", IdentifierField),
    ('signature_type', LimitedLengthStringField),
    ('tag', LimitedLengthStringField),
])


@pytest.mark.types
def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientClaimDefGetOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


@pytest.mark.types
def test_has_expected_validators():
    schema = dict(ClientClaimDefGetOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
