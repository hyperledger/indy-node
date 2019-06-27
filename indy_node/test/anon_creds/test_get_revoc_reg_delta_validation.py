import pytest
import copy
from indy_common.types import SafeRequest
from indy_common.constants import REVOC_REG_DEF_ID
from indy_common.constants import FROM, TO
from indy_common.types import Request
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest


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


def test_revoc_reg_delta_from_greater_then_to(create_node_and_not_start,
                                              build_get_revoc_reg_delta):
    node = create_node_and_not_start
    req = build_get_revoc_reg_delta
    req['operation'][FROM] = 100
    req['operation'][TO] = 20
    with pytest.raises(InvalidClientRequest, match="Timestamp FROM more then TO"):
        node.read_manager.static_validation(Request(**req))
