from collections import OrderedDict
from indy_common.types import RevocDefValueField, ClientRevocDefSubmitField
from plenum.common.messages.fields import IntegerField, AnyMapField, NonEmptyStringField, ConstantField, ChooseField, \
    LimitedLengthStringField
from indy_common.constants import ISSUANCE_TYPE, MAX_CRED_NUM, PUBLIC_KEYS, \
    TAILS_LOCATION, TAILS_HASH, ID, REVOC_TYPE, TXN_TYPE, TAG, CRED_DEF_ID, VALUE


EXPECTED_REVOC_DEF_VALUE_FIELDS = OrderedDict([
    (ISSUANCE_TYPE, ChooseField),
    (MAX_CRED_NUM, IntegerField),
    (PUBLIC_KEYS, AnyMapField),
    (TAILS_HASH, NonEmptyStringField),
    (TAILS_LOCATION, NonEmptyStringField),
])

EXPECTED_REVOC_DEF_SUBMIT_FIELDS = OrderedDict([
    (TXN_TYPE, ConstantField),
    (ID, NonEmptyStringField),
    (REVOC_TYPE, LimitedLengthStringField),
    (TAG, LimitedLengthStringField),
    (CRED_DEF_ID, NonEmptyStringField),
    (VALUE, RevocDefValueField)
])


def test_revoc_value_has_expected_fields():
    actual_field_names = OrderedDict(
        RevocDefValueField.schema).keys()
    assert actual_field_names == EXPECTED_REVOC_DEF_VALUE_FIELDS.keys()


def test_revoc_value_has_expected_validators():
    schema = dict(RevocDefValueField.schema)
    for field, validator in EXPECTED_REVOC_DEF_VALUE_FIELDS.items():
        assert isinstance(schema[field], validator)


def test_client_submit_has_expected_fields():
    actual_field_names = OrderedDict(
        ClientRevocDefSubmitField.schema).keys()
    assert actual_field_names == EXPECTED_REVOC_DEF_SUBMIT_FIELDS.keys()


def test_client_submit_has_expected_validators():
    schema = dict(ClientRevocDefSubmitField.schema)
    for field, validator in EXPECTED_REVOC_DEF_SUBMIT_FIELDS.items():
        assert isinstance(schema[field], validator)
