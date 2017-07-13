import pytest
from sovrin_common.types import ClientDiscloOperation
from collections import OrderedDict
from plenum.common.messages.fields import ConstantField, NonEmptyStringField, IdentifierField


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("data", NonEmptyStringField),
    ('nonce', NonEmptyStringField),
    ("dest", IdentifierField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientDiscloOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientDiscloOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
