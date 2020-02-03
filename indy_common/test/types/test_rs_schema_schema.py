from collections import OrderedDict

from indy_common.types import RsSchemaMetaField, ClientSetRsSchemaOperation, SetRsSchemaDataField, RsSchemaField
from plenum.common.messages.fields import ConstantField, VersionField, LimitedLengthStringField

EXPECTED_SCHEMA_META_FIELDS = OrderedDict([
    ("name", LimitedLengthStringField),
    ("version", VersionField),
    ("type", ConstantField),
])


def test_meta_has_expected_fields_s():
    actual_field_names = OrderedDict(RsSchemaMetaField.schema).keys()
    assert actual_field_names == EXPECTED_SCHEMA_META_FIELDS.keys()


def test_meta_has_expected_validators_s():
    schema = dict(RsSchemaMetaField.schema)
    for field, validator in EXPECTED_SCHEMA_META_FIELDS.items():
        assert isinstance(schema[field], validator)


'''Schema:{
        "@context": {}, ## optional, could be in expanded form
        "@type":"",
        "@id":"",
    }
## TODO: check for this in static validation and test here.
EXPECTED_RS_SCHEMA_FIELDS = OrderedDict([
    ('@type', LimitedLengthStringField),
    ('@id', LimitedLengthStringField),
])'''
EXPECTED_RS_SCHEMA_DATA_FIELDS = OrderedDict([
    ('schema', RsSchemaField),
])


def test_data_has_expected_fields_s():
    actual_field_names = OrderedDict(SetRsSchemaDataField.schema).keys()
    assert actual_field_names == EXPECTED_RS_SCHEMA_DATA_FIELDS.keys()


def test_data_has_expected_validators_s():
    schema = dict(SetRsSchemaDataField.schema)
    for field, validator in EXPECTED_RS_SCHEMA_DATA_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_RS_SCHEMA_TXN_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("meta", RsSchemaMetaField),
    ("data", SetRsSchemaDataField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientSetRsSchemaOperation.schema).keys()
    assert actual_field_names == EXPECTED_RS_SCHEMA_TXN_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientSetRsSchemaOperation.schema)
    for field, validator in EXPECTED_RS_SCHEMA_TXN_FIELDS.items():
        assert isinstance(schema[field], validator)
