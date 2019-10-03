from collections import OrderedDict

from indy_common.types import ClientSchemaOperation, SetContextMetaField, SetContextDataField, \
    ClientSetContextOperation, ContextField
from plenum.common.messages.fields import ConstantField, VersionField, IterableField, LimitedLengthStringField

EXPECTED_ORDERED_CONTEXT_META_FIELDS = OrderedDict([
    ("name", LimitedLengthStringField),
    ("version", VersionField),
    ("type", ConstantField),
])


def test_meta_has_expected_fields_s():
    actual_field_names = OrderedDict(SetContextMetaField.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_CONTEXT_META_FIELDS.keys()


def test_meta_has_expected_validators_s():
    schema = dict(SetContextMetaField.schema)
    for field, validator in EXPECTED_ORDERED_CONTEXT_META_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_ORDERED_CONTEXT_DATA_FIELDS = OrderedDict([
    ("@context", ContextField),
])


def test_data_has_expected_fields_s():
    actual_field_names = OrderedDict(SetContextDataField.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_CONTEXT_DATA_FIELDS.keys()


def test_data_has_expected_validators_s():
    schema = dict(SetContextDataField.schema)
    for field, validator in EXPECTED_ORDERED_CONTEXT_DATA_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("meta", SetContextMetaField),
    ("data", SetContextDataField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientSetContextOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientSetContextOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)
