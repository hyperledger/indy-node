from collections import OrderedDict
from indy_common.types import ClientGetRevocRegDeltaField
from plenum.common.messages.fields import NonEmptyStringField, ConstantField, IntegerField
from indy_common.constants import TXN_TYPE, REVOC_REG_DEF_ID, FROM, TO, GET_REVOC_REG_DELTA


EXPECTED_GET_REVOC_REG_DELTA_FIELD = OrderedDict([
    (TXN_TYPE, ConstantField(GET_REVOC_REG_DELTA)),
    (REVOC_REG_DEF_ID, NonEmptyStringField),
    (FROM, IntegerField),
    (TO, IntegerField),
])


def test_get_revoc_reg_def_schema():
    actual_field_name = OrderedDict(ClientGetRevocRegDeltaField.schema).keys()
    assert EXPECTED_GET_REVOC_REG_DELTA_FIELD.keys() == actual_field_name
