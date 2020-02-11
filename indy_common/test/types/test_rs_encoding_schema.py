from collections import OrderedDict

from indy_common.types import ClientSetRsEncodingOperation, SetRsEncodingDataField, \
    SetRsEncodingOpDataField, SetRsEncodingContentField, HashField, SetRsEncodingField, Puts, EncodingAlgorithm
from plenum.common.messages.fields import ConstantField, VersionField, LimitedLengthStringField, IdentifierField

EXPECTED_ENCODING_OP_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("data", SetRsEncodingOpDataField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientSetRsEncodingOperation.schema).keys()
    assert actual_field_names == EXPECTED_ENCODING_OP_FIELDS.keys()

def test_has_expected_validators():
    schema = dict(ClientSetRsEncodingOperation.schema)
    for field, validator in EXPECTED_ENCODING_OP_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_ENCODING_OP_DATA_FIELDS = OrderedDict([
    ("id", IdentifierField),
    ("content", SetRsEncodingContentField),
])


def test_meta_has_expected_fields_s():
    actual_field_names = OrderedDict(SetRsEncodingOpDataField.schema).keys()
    assert actual_field_names == EXPECTED_ENCODING_OP_DATA_FIELDS.keys()


def test_meta_has_expected_validators_s():
    schema = dict(SetRsEncodingOpDataField.schema)
    for field, validator in EXPECTED_ENCODING_OP_DATA_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_ENCODING_CONTENT_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("name", LimitedLengthStringField),
    ("version", VersionField),
    ("hash", HashField),
    ("data", SetRsEncodingDataField),
])


def test_meta_has_expected_fields_s():
    actual_field_names = OrderedDict(SetRsEncodingContentField.schema).keys()
    assert actual_field_names == EXPECTED_ENCODING_CONTENT_FIELDS.keys()


def test_meta_has_expected_validators_s():
    schema = dict(SetRsEncodingContentField.schema)
    for field, validator in EXPECTED_ENCODING_CONTENT_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_RS_ENCODING_DATA_FIELDS = OrderedDict([
    ("encoding", SetRsEncodingField),
])


def test_data_has_expected_fields_s():
    actual_field_names = OrderedDict(SetRsEncodingDataField.schema).keys()
    assert actual_field_names == EXPECTED_RS_ENCODING_DATA_FIELDS.keys()


def test_data_has_expected_validators_s():
    schema = dict(SetRsEncodingDataField.schema)
    for field, validator in EXPECTED_RS_ENCODING_DATA_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_RS_ENCODING_FIELDS = OrderedDict([
    ("input", Puts),
    ("output", Puts),
    ("algorithm", EncodingAlgorithm),
    ("test_vectors", LimitedLengthStringField),
])


def test_data_has_expected_fields_s():
    actual_field_names = OrderedDict(SetRsEncodingDataField.schema).keys()
    assert actual_field_names == EXPECTED_RS_ENCODING_FIELDS.keys()


def test_data_has_expected_validators_s():
    schema = dict(SetRsEncodingDataField.schema)
    for field, validator in EXPECTED_RS_ENCODING_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_RS_INPUTS_FIELDS = OrderedDict([
    ("id", LimitedLengthStringField),
    ("type", LimitedLengthStringField),
])


def test_data_has_expected_fields_s():
    actual_field_names = OrderedDict(Puts.schema).keys()
    assert actual_field_names == EXPECTED_RS_INPUTS_FIELDS.keys()


def test_data_has_expected_validators_s():
    schema = dict(Puts.schema)
    for field, validator in EXPECTED_RS_INPUTS_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_RS_ALGORITHM_FIELDS = OrderedDict([
    ("description", LimitedLengthStringField),
    ("documentation", LimitedLengthStringField),
    ("implementation", LimitedLengthStringField),
])


def test_data_has_expected_fields_s():
    actual_field_names = OrderedDict(EncodingAlgorithm.schema).keys()
    assert actual_field_names == EXPECTED_RS_ALGORITHM_FIELDS.keys()


def test_data_has_expected_validators_s():
    schema = dict(EncodingAlgorithm.schema)
    for field, validator in EXPECTED_RS_ALGORITHM_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_ENCODING_HASH_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("value", LimitedLengthStringField)
])


def test_data_has_expected_fields_s():
    actual_field_names = OrderedDict(HashField.schema).keys()
    assert actual_field_names == EXPECTED_ENCODING_HASH_FIELDS.keys()


def test_data_has_expected_validators_s():
    schema = dict(HashField.schema)
    for field, validator in EXPECTED_ENCODING_HASH_FIELDS.items():
        assert isinstance(schema[field], validator)