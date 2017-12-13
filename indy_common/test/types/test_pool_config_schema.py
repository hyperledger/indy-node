import pytest
from indy_common.types import ClientPoolConfigOperation
from collections import OrderedDict
from plenum.common.messages.fields import ConstantField, BooleanField


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("writes", BooleanField),
    ("force", BooleanField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientPoolConfigOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientPoolConfigOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
