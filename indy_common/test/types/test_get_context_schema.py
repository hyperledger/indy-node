from collections import OrderedDict

from indy_common.types import ClientGetContextOperation, GetContextField
from plenum.common.messages.fields import ConstantField, IdentifierField, VersionField, LimitedLengthStringField

EXPECTED_ORDERED_FIELDS_SCHEMA = OrderedDict([
    ("name", LimitedLengthStringField),
    ("version", VersionField)
])


def test_has_expected_fields_s():
    actual_field_names = OrderedDict(GetContextField.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS_SCHEMA.keys()


def test_has_expected_validators_s():
    schema = dict(GetContextField.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS_SCHEMA.items():
        assert isinstance(schema[field], validator)


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("dest", IdentifierField),
    ('meta', GetContextField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientGetContextOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientGetContextOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
