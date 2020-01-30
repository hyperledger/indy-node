from collections import OrderedDict

from indy_common.types import ClientRsClaimDefGetOperation, RsClaimDefMetaField
from plenum.common.messages.fields import ConstantField, LimitedLengthStringField, TxnSeqNoField, IdentifierField, \
    VersionField

EXPECTED_ORDERED_META_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("name", LimitedLengthStringField),
    ("version", VersionField),
])


def test_has_expected_fields_s():
    actual_field_names = OrderedDict(RsClaimDefMetaField.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_META_FIELDS.keys()


def test_has_expected_validators_s():
    schema = dict(RsClaimDefMetaField.schema)
    for field, validator in EXPECTED_ORDERED_META_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_ORDERED_CLAIM_DEF_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("ref", TxnSeqNoField),
    ("issuer", IdentifierField),
    ('mapping', LimitedLengthStringField),
    ('signature_type', LimitedLengthStringField),
    ('tag', LimitedLengthStringField),
    ('@context', LimitedLengthStringField),
    ('@id', LimitedLengthStringField),
    ('@type', LimitedLengthStringField),
    ('tag', LimitedLengthStringField),
])

def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientRsClaimDefGetOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientRsClaimDefGetOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)


EXPECTED_ORDERED_OPERATION_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("from", IdentifierField),
    ("meta", RsClaimDefMetaField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientRsClaimDefGetOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_OPERATION_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientRsClaimDefGetOperation.schema)
    for field, validator in EXPECTED_ORDERED_OPERATION_FIELDS.items():
        assert isinstance(schema[field], validator)