import pytest

from indy_common.types import ClientClaimDefSubmitOperation, ClaimDefField
from collections import OrderedDict
from plenum.common.messages.fields import ConstantField, LimitedLengthStringField, TxnSeqNoField, AnyMapField

EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("ref", TxnSeqNoField),
    ("data", ClaimDefField),
    ("signature_type", LimitedLengthStringField),
    ("tag", LimitedLengthStringField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(
        ClientClaimDefSubmitOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientClaimDefSubmitOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_DATA_FIELDS = OrderedDict([
    ("primary", AnyMapField),
    ("revocation", AnyMapField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(
        ClaimDefField.schema).keys()
    assert actual_field_names == EXPECTED_DATA_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClaimDefField.schema)
    for field, validator in EXPECTED_DATA_FIELDS.items():
        assert isinstance(schema[field], validator)
