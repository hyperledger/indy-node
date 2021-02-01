from collections import OrderedDict

import pytest

from indy_common.types import ClientGetSchemaOperation, GetSchemaField
from plenum.common.messages.fields import ConstantField, IdentifierField, VersionField, LimitedLengthStringField

EXPECTED_ORDERED_FIELDS_SCHEMA = OrderedDict([
    ("name", LimitedLengthStringField),
    ("version", VersionField),
    ('origin', IdentifierField),
])


@pytest.mark.types
def test_has_expected_fields_s():
    actual_field_names = OrderedDict(GetSchemaField.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS_SCHEMA.keys()


@pytest.mark.types
def test_has_expected_validators_s():
    schema = dict(GetSchemaField.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS_SCHEMA.items():
        assert isinstance(schema[field], validator)


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("dest", IdentifierField),
    ('data', GetSchemaField),
])


@pytest.mark.types
def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientGetSchemaOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


@pytest.mark.types
def test_has_expected_validators():
    schema = dict(ClientGetSchemaOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
