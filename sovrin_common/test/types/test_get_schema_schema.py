import pytest
from sovrin_common.types import SchemaField, ClientGetSchemaOperation
from collections import OrderedDict
from plenum.common.messages.fields import ConstantField, NonEmptyStringField, IdentifierField, VersionField


EXPECTED_ORDERED_FIELDS_s = OrderedDict([
    ("name", NonEmptyStringField),
    ("version", VersionField),
    ('origin', NonEmptyStringField),
])


def test_has_expected_fields_s():
    actual_field_names = OrderedDict(SchemaField.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS_s.keys()


def test_has_expected_validators_s():
    schema = dict(SchemaField.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS_s.items():
        assert isinstance(schema[field], validator)


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("dest", IdentifierField),
    ('data', SchemaField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientGetSchemaOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientGetSchemaOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)





