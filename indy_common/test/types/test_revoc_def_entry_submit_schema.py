from collections import OrderedDict
from indy_common.types import RevocRegEntryValueField, ClientRevocRegEntrySubmitField
from plenum.common.messages.fields import NonEmptyStringField, IterableField, ConstantField
from indy_common.constants import REVOC_REG_DEF_ID, REVOC_TYPE, VALUE, PREV_ACCUM, \
    ACCUM, ISSUED, REVOKED, TXN_TYPE


EXPECTED_REVOC_DEF_ENTRY_VALUE_FIELDS = OrderedDict([
    (PREV_ACCUM, NonEmptyStringField),
    (ACCUM, NonEmptyStringField),
    (ISSUED, IterableField),
    (REVOKED, IterableField),
])

EXPECTED_REVOC_DEF_ENTRY_SUBMIT_FIELDS = OrderedDict([
    (TXN_TYPE, ConstantField),
    (REVOC_REG_DEF_ID, NonEmptyStringField),
    (REVOC_TYPE, NonEmptyStringField),
    (VALUE, RevocRegEntryValueField)
])


def test_revoc_entry_value_has_expected_fields():
    actual_field_names = OrderedDict(
        RevocRegEntryValueField.schema).keys()
    assert actual_field_names == EXPECTED_REVOC_DEF_ENTRY_VALUE_FIELDS.keys()


def test_revoc_entry_value_has_expected_validators():
    schema = dict(RevocRegEntryValueField.schema)
    for field, validator in EXPECTED_REVOC_DEF_ENTRY_VALUE_FIELDS.items():
        assert isinstance(schema[field], validator)


def test_client_revoc_entry_submit_has_expected_fields():
    actual_field_names = OrderedDict(
        ClientRevocRegEntrySubmitField.schema).keys()
    assert actual_field_names == EXPECTED_REVOC_DEF_ENTRY_SUBMIT_FIELDS.keys()


def test_client_revoc_entry_submit_has_expected_validators():
    schema = dict(ClientRevocRegEntrySubmitField.schema)
    for field, validator in EXPECTED_REVOC_DEF_ENTRY_SUBMIT_FIELDS.items():
        assert isinstance(schema[field], validator)
