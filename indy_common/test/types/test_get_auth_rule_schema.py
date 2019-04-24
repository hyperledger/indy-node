from collections import OrderedDict

from indy_common.types import ClientGetAuthRuleOperation, AuthRuleValueField
from plenum.common.messages.fields import ConstantField, LimitedLengthStringField, ChooseField

EXPECTED_ORDERED_FIELDS = OrderedDict([
    ("type", ConstantField),
    ("auth_action", ChooseField),
    ("auth_type", LimitedLengthStringField),
    ("field", LimitedLengthStringField),
    ("old_value", AuthRuleValueField),
    ("new_value", AuthRuleValueField),
])


def test_has_expected_fields():
    actual_field_names = OrderedDict(ClientGetAuthRuleOperation.schema).keys()
    assert actual_field_names == EXPECTED_ORDERED_FIELDS.keys()


def test_has_expected_validators():
    schema = dict(ClientGetAuthRuleOperation.schema)
    for field, validator in EXPECTED_ORDERED_FIELDS.items():
        assert isinstance(schema[field], validator)


def test_attrib_with_empty_enc_fails():
    validator = AuthRuleValueField()
    value = ''
    validator.validate(value)
    value = None
    validator.validate(value)
