from collections import OrderedDict

from indy_common.types import ClientSetRsCredDefOperation, RsCredDefMetaField, RsCredDefField, SetRsCredDefDataField
from plenum.common.messages.fields import ConstantField, LimitedLengthStringField, TxnSeqNoField, IdentifierField, \
    VersionField, AnyMapField

EXPECTED_ORDERED_META_FIELDS = OrderedDict([
    ("name", LimitedLengthStringField),
    ("type", ConstantField),
    ("version", VersionField),  # instead of a tag we have a version
])


def test_has_expected_fields_s():
    actual_field_names = OrderedDict(RsCredDefMetaField.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_META_FIELDS.keys()


def test_has_expected_validators_s():
    schema = dict(RsCredDefMetaField.schema)
    for field, validator in EXPECTED_ORDERED_META_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_CLAIM_DEF_FIELDS = OrderedDict([
    ("@id", LimitedLengthStringField),
    ("@type", LimitedLengthStringField),
    ("@context_ref", TxnSeqNoField),
    ("mapping_ref", TxnSeqNoField),
    ("issuer", IdentifierField),
    ("signature_type", LimitedLengthStringField),
    ("primary", AnyMapField),
    ("revocation", AnyMapField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(RsCredDefField.schema).keys()
    assert actual_field_names == EXPECTED_CLAIM_DEF_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(RsCredDefField.schema)
    for field, validator in EXPECTED_CLAIM_DEF_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_DATA_FIELDS = OrderedDict([
    ("data", SetRsCredDefDataField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientSetRsCredDefOperation.schema).keys()
    assert actual_field_names == EXPECTED_OP_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientSetRsCredDefOperation.schema)
    for field, validator in EXPECTED_OP_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_OP_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("meta", RsCredDefMetaField),
    ("data", RsCredDefField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientSetRsCredDefOperation.schema).keys()
    assert actual_field_names == EXPECTED_OP_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientSetRsCredDefOperation.schema)
    for field, validator in EXPECTED_OP_FIELDS.items():
        assert isinstance(schema[field], validator)


'''
"type": "203",
"meta": {
    "name": "name",
    "version": "version",
    "type": "cred_def"
},
"data":{
    cred_def : {
      "@context_ref": "ctx:sov:44bBhN4mwLJQQCCS2CG9f53JsuyqLwz3MtxM9uLw",
      "@id": "cdf:sov:Q6kuSqnxE57waPFs2xAs7q:3:CL:12:CDL1",
      "@type": "sch:sov:22KpkXgecryx9k7N6XN1QoN3gXwBkSU8SfyyYQG",
      "issuer": "did:sov:4t1FPo72LzDMwpqtTVGVjysD6GUqS",
      "mapping_ref": "map:sov:WqfHp5rsWoVGEA7tkSn8ZVpZcLZvfNJG4JmRg7EvJmGEA",
      "publicKey":{
        "n": "0x39...A1D",
        "S": "0x29...2A6",
        "Z": "0x12...4D6",
        "R":{
          "Ra39":
            "0x21...F3"
        }
      }
    }
}
'''