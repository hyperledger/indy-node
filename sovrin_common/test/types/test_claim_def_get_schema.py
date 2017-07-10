import pytest
from sovrin_common.types import ClientClaimDefGetOperation
from collections import OrderedDict
from plenum.common.messages.fields import ConstantField, NonEmptyStringField, TxnSeqNoField


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("ref", TxnSeqNoField),
    ("origin", NonEmptyStringField),
    ('signature_type', NonEmptyStringField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientClaimDefGetOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientClaimDefGetOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
