import pytest
from sovrin_common.types import ClientAttribOperation
from collections import OrderedDict
from plenum.common.messages.fields import ConstantField, NonEmptyStringField, IdentifierField, JsonField


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("dest", IdentifierField),
    ("raw", JsonField),
    ('enc', NonEmptyStringField),
    ('hash', NonEmptyStringField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientAttribOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientAttribOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
