from collections import OrderedDict
from indy_common.types import ClientGetRevocRegField
from plenum.common.messages.fields import NonEmptyStringField, ConstantField, IntegerField
from indy_common.constants import TXN_TYPE, REVOC_REG_DEF_ID, TIMESTAMP, GET_REVOC_REG


EXPECTED_GET_REVOC_REG_FIELD = OrderedDict([
    (REVOC_REG_DEF_ID, NonEmptyStringField),
    (TIMESTAMP, IntegerField),
    (TXN_TYPE, ConstantField(GET_REVOC_REG))
])


def test_get_revoc_reg_def_schema():
    actual_field_name = OrderedDict(ClientGetRevocRegField.schema).keys()
    assert EXPECTED_GET_REVOC_REG_FIELD.keys() == actual_field_name
