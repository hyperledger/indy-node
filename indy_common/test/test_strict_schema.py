from indy_common.types import SafeRequest
from plenum.common.constants import CURRENT_PROTOCOL_VERSION, TXN_TYPE, TARGET_NYM, VERKEY, NYM
from plenum.common.types import f, OPERATION
from plenum.test.input_validation.constants import TEST_TARGET_NYM, TEST_VERKEY_ABBREVIATED


def test_client_safe_req_not_strict_by_default():
    operation = {
        TXN_TYPE: NYM,
        TARGET_NYM: TEST_TARGET_NYM,
        VERKEY: TEST_VERKEY_ABBREVIATED,
        "some_new_field_op1": "some_new_value_op1",
        "some_new_field_op2": "some_new_value_op2"
    }
    kwargs = {f.IDENTIFIER.nm: "1" * 16,
              f.REQ_ID.nm: 1,
              OPERATION: operation,
              f.SIG.nm: "signature",
              f.PROTOCOL_VERSION.nm: CURRENT_PROTOCOL_VERSION,
              "some_new_field1": "some_new_value1",
              "some_new_field2": "some_new_value2"}
    assert SafeRequest(**kwargs)
