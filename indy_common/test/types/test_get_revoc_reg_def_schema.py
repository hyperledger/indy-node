from collections import OrderedDict
from indy_common.types import ClientGetRevocRegDefField
from plenum.common.messages.fields import NonEmptyStringField, ConstantField
from indy_common.constants import ID, TXN_TYPE, REVOC_TYPE


EXPECTED_GET_REVOC_REG_DEF_FIELD = OrderedDict([
    (ID, NonEmptyStringField()),
    (TXN_TYPE, ConstantField),
])


def test_get_revoc_reg_def_schema():
    actual_field_name = OrderedDict(ClientGetRevocRegDefField.schema).keys()
    assert EXPECTED_GET_REVOC_REG_DEF_FIELD.keys() == actual_field_name
