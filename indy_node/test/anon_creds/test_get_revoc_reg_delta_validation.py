import pytest
import copy
from indy_common.types import SafeRequest
from indy_common.constants import REVOC_REG_DEF_ID, FROM


def test_revoc_reg_delta_schema_validation_wrong_type(build_get_revoc_reg_delta):
    req = copy.deepcopy(build_get_revoc_reg_delta)
    req['operation'][FROM] = "10"
    with pytest.raises(TypeError, match="expected types 'int', got 'str'"):
        SafeRequest(**req)


def test_revoc_reg_delta_schema_validation_missed_fields(build_get_revoc_reg_delta):
    req = copy.deepcopy(build_get_revoc_reg_delta)
    del req['operation'][REVOC_REG_DEF_ID]
    with pytest.raises(TypeError, match="missed fields - {}".format(REVOC_REG_DEF_ID)):
        SafeRequest(**req)
