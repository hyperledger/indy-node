from collections import OrderedDict

from indy_common.types import ClientSetRsMappingOperation, RsMappingMetaField, RsMappingField, SetRsMappingDataField, RsMappingAttributeField, \
    ContextField, RsMappingAttributeField
from plenum.common.messages.fields import ConstantField, LimitedLengthStringField, \
    VersionField, AnyMapField, IterableField

MAPPING_META_FIELDS = OrderedDict([
    ("name", LimitedLengthStringField),
    ("type", ConstantField),
    ("version", VersionField),
])


def test_has_expected_fields_s():
    actual_field_names = OrderedDict(RsMappingMetaField.schema).keys()
    assert actual_field_names == MAPPING_META_FIELDS.keys()


def test_has_expected_validators_s():
    schema = dict(RsMappingMetaField.schema)
    for field, validator in MAPPING_META_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_MAPPING_FIELDS = OrderedDict([
    ("@id", LimitedLengthStringField),
    ("@type", LimitedLengthStringField),
    ("@context", ContextField),
    ("schemas", IterableField),
    ("attribute_map", RsMappingAttributeField)
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(RsMappingField.schema).keys()
    assert actual_field_names == EXPECTED_MAPPING_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(RsMappingField.schema)
    for field, validator in EXPECTED_MAPPING_FIELDS.items():
        assert isinstance(schema[field], validator)


'''EXPECTED_DATA_FIELDS = OrderedDict([  # MappingAttributeField
    ("graph_path", AnyMapField),  # could just be a list that represents path to attrib
    ("encoding", LimitedLengthStringField)
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(RsMappingAttributeField.schema).keys()
    assert actual_field_names == EXPECTED_OP_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(RsMappingAttributeField.schema)
    for field, validator in EXPECTED_OP_FIELDS.items():
        assert isinstance(schema[field], validator)'''


EXPECTED_OP_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("meta", RsMappingMetaField),
    ("data", SetRsMappingDataField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientSetRsMappingOperation.schema).keys()
    assert actual_field_names == EXPECTED_OP_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientSetRsMappingOperation.schema)
    for field, validator in EXPECTED_OP_FIELDS.items():
        assert isinstance(schema[field], validator)


'''
"type": "204",
"meta": {
    "name": "name",
    "version": "version",
    "type": "mapping"
},
"data":{
    mapping : {
        "@context": "ctx:sov:44bBhN4mwLJQQCCS2CG9f53JsuyqLwz3MtxM9uLw",
        "@id": "cdf:sov:Q6kuSqnxE57waPFs2xAs7q:3:CL:12:CDL1",
        "@type": "sch:sov:22KpkXgecryx9k7N6XN1QoN3gXwBkSU8SfyyYQG",
        "schemas":[...],
        "attributes": ["<uri>","<uri>"]
    }
}
'''