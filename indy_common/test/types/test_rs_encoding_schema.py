from collections import OrderedDict

from indy_common.types import RsEncodingMetaField, ClientSetRsEncodingOperation, SetRsEncodingDataField
from plenum.common.messages.fields import ConstantField, VersionField, LimitedLengthStringField

EXPECTED_ENCODING_META_FIELDS = OrderedDict([
    ("name", LimitedLengthStringField),
    ("version", VersionField),
    ("type", ConstantField),
])


def test_meta_has_expected_fields_s():
    actual_field_names = OrderedDict(RsEncodingMetaField.schema).keys()
    assert actual_field_names == EXPECTED_ENCODING_META_FIELDS.keys()


def test_meta_has_expected_validators_s():
    schema = dict(RsEncodingMetaField.schema)
    for field, validator in EXPECTED_ENCODING_META_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_RS_ENCODING_DATA_FIELDS = OrderedDict([
    ("encoding", LimitedLengthStringField),
])


def test_data_has_expected_fields_s():
    actual_field_names = OrderedDict(SetRsEncodingDataField.schema).keys()
    assert actual_field_names == EXPECTED_RS_ENCODING_DATA_FIELDS.keys()


def test_data_has_expected_validators_s():
    schema = dict(SetRsEncodingDataField.schema)
    for field, validator in EXPECTED_RS_ENCODING_DATA_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_RS_ENCODING_TXN_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("meta", RsEncodingMetaField),
    ("data", SetRsEncodingDataField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientSetRsEncodingOperation.schema).keys()
    assert actual_field_names == EXPECTED_RS_ENCODING_TXN_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientSetRsEncodingOperation.schema)
    for field, validator in EXPECTED_RS_ENCODING_TXN_FIELDS.items():
        assert isinstance(schema[field], validator)
