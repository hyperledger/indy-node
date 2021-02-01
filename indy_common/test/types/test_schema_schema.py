from collections import OrderedDict

import pytest

from indy_common.types import ClientSchemaOperation, SchemaField
from plenum.common.messages.fields import ConstantField, VersionField, IterableField, LimitedLengthStringField

EXPECTED_ORDERED_FIELDS_SCHEMA = OrderedDict([
    ("name", LimitedLengthStringField),
    ("version", VersionField),
    ("attr_names", IterableField),
])


@pytest.mark.types
def test_has_expected_fields_s():
    actual_field_names = OrderedDict(SchemaField.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS_SCHEMA.keys()


@pytest.mark.types
def test_has_expected_validators_s():
    schema = dict(SchemaField.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS_SCHEMA.items():
        assert isinstance(schema[field], validator)


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("data", SchemaField),
])


@pytest.mark.types
def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientSchemaOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


@pytest.mark.types
def test_has_expected_validators():
    schema = dict(ClientSchemaOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
