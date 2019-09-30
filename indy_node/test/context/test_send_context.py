import pytest

from indy_common.config import CONTEXT_SIZE_LIMIT
from plenum.common.constants import DATA

from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.constants import CONTEXT_NAME, CONTEXT_VERSION, RS_TYPE, CONTEXT_TYPE, META, \
    SET_CONTEXT
from indy_node.test.context.helper import W3C_BASE_CONTEXT, SCHEMA_ORG_CONTEXT, EXCESSIVELY_BIG_CONTEXT
from indy_common.types import SetContextMetaField, SetContextDataField, ClientSetContextOperation
from indy_node.test.api.helper import validate_write_reply, sdk_write_context_and_check
from plenum.common.exceptions import RequestRejectedException


def test_send_context_pass(looper, sdk_pool_handle,
                                     sdk_wallet_endorser):
    rep = sdk_write_context_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_endorser,
        SCHEMA_ORG_CONTEXT,
        "Base_Context1",
        "1.0"
    )
    meta = rep[0][0]['operation'][META]
    assert meta[CONTEXT_VERSION] == '1.0'
    assert meta[CONTEXT_NAME] == 'Base_Context1'
    assert meta[RS_TYPE] == CONTEXT_TYPE
    data = rep[0][0]['operation'][DATA]
    assert data == SCHEMA_ORG_CONTEXT


def test_write_same_context_returns_same_response(looper, sdk_pool_handle, sdk_wallet_endorser):
    rep1 = sdk_write_context_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_endorser,
        W3C_BASE_CONTEXT,
        "Base_Context2",
        "1.0"
    )
    rep2 = sdk_write_context_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_endorser,
        W3C_BASE_CONTEXT,
        "Base_Context2",
        "1.0"
    )
    assert rep1==rep2


def test_write_same_context_with_different_reqid_fails(looper, sdk_pool_handle, sdk_wallet_endorser):
    sdk_write_context_and_check(
        looper, sdk_pool_handle,
        sdk_wallet_endorser,
        SCHEMA_ORG_CONTEXT,
        "Base_Context3",
        "1.0",
        1234
    )
    with pytest.raises(RequestRejectedException,
                       match=str(AuthConstraintForbidden())):
        resp = sdk_write_context_and_check(
            looper, sdk_pool_handle,
            sdk_wallet_endorser,
            SCHEMA_ORG_CONTEXT,
            "Base_Context3",
            "1.0",
            2345
        )
        validate_write_reply(resp)


def test_context_over_maximum_size():
    context = SetContextDataField()
    with pytest.raises(TypeError) as ex_info:
        context.validate(EXCESSIVELY_BIG_CONTEXT)
    ex_info.match(
        "size should be at most {}".format(CONTEXT_SIZE_LIMIT)
    )


def test_validate_meta_fail_on_empty():
    meta = SetContextMetaField()
    with pytest.raises(TypeError) as e:
        meta.validate({})
    assert "validation error [SetContextMetaField]: missed fields" in str(e.value)
    assert "name" in str(e.value)
    assert "version" in str(e.value)
    assert "type" in str(e.value)


def test_validate_meta_fail_no_name():
    meta = SetContextMetaField()
    with pytest.raises(TypeError) as e:
        meta.validate({
            "version": "2.5",
            "type": "ctx"
        })
    assert "validation error [SetContextMetaField]: missed fields" in str(e.value)
    assert "name" in str(e.value)


def test_validate_meta_fail_no_version():
    meta = SetContextMetaField()
    with pytest.raises(TypeError) as e:
        meta.validate({
            "name": "New Context",
            "type": "ctx"
        })
    assert "validation error [SetContextMetaField]: missed fields" in str(e.value)
    assert "version" in str(e.value)


def test_validate_meta_fail_invalid_version():
    meta = SetContextMetaField()
    with pytest.raises(TypeError) as e:
        meta.validate({
            "name": "New Context",
            "type": "ctx",
            "version": "A"
        })
    assert "validation error [SetContextMetaField]: Invalid version: 'A' (version=A)" in str(e.value)


def test_validate_meta_fail_no_type():
    meta = SetContextMetaField()
    with pytest.raises(TypeError) as e:
        meta.validate({
            "name": "New Context",
            "version": "2.5"
        })
    assert "validation error [SetContextMetaField]: missed fields" in str(e.value)
    assert "type" in str(e.value)


def test_validate_meta_fail_wrong_type():
    meta = SetContextMetaField()
    with pytest.raises(TypeError) as e:
        meta.validate({
            "name": "New Context",
            "version": "2.5",
            "type": "sch"
        })
    assert "validation error [SetContextMetaField]: has to be equal ctx (type=sch)" in str(e.value)


def test_validate_meta_pass():
    meta = SetContextMetaField()
    meta.validate({
        "name": "New Context",
        "version": "5.2",
        "type": "ctx"
    })


def test_validate_data_fail_on_empty():
    data = SetContextDataField()
    with pytest.raises(TypeError) as e:
        data.validate({})
    assert "validation error [SetContextDataField]: missed fields" in str(e.value)
    assert "@context" in str(e.value)


def test_validate_data_fail_not_dict():
    data = SetContextDataField()
    with pytest.raises(TypeError) as e:
        data.validate("context")
    assert "validation error [SetContextDataField]: invalid type <class 'str'>, dict expected" in str(e.value)


def test_validate_data_fail_no_context_property():
    data = SetContextDataField()
    with pytest.raises(TypeError) as e:
        data.validate({
            "name": "Thing"
        })
    assert "validation error [SetContextDataField]: missed fields - @context" in str(e.value)


def test_validate_data_pass():
    data = SetContextDataField()
    data.validate({"@context": "https://www.example.com"})


def test_validate_operation_fail_no_meta():
    operation = ClientSetContextOperation()
    with pytest.raises(TypeError) as e:
        operation.validate({
            "data": W3C_BASE_CONTEXT,
            "type": SET_CONTEXT
        })
    assert 'validation error [ClientSetContextOperation]: missed fields - meta' in str(e.value)


def test_validate_operation_fail_no_data():
    operation = ClientSetContextOperation()
    with pytest.raises(TypeError) as e:
        operation.validate({
            "meta": {
                "type": CONTEXT_TYPE,
                "name": "TestContext",
                "version": "1.0"
            },
            "type": SET_CONTEXT
        })
    assert "validation error [ClientSetContextOperation]: missed fields - data." in str(e.value)


def test_validate_operation_fail_no_type():
    operation = ClientSetContextOperation()
    with pytest.raises(TypeError) as e:
        operation.validate({
            "meta": {
                "type": CONTEXT_TYPE,
                "name": "TestContext",
                "version": "1.0"
            },
            "data": W3C_BASE_CONTEXT
        })
    assert "validation error [ClientSetContextOperation]: missed fields - type." in str(e.value)


def test_validate_operation_pass():
    operation = ClientSetContextOperation()
    operation.validate({
        "meta": {
            "type": CONTEXT_TYPE,
            "name": "TestContext",
            "version": "1.0"
        },
        "data": W3C_BASE_CONTEXT,
        "type": SET_CONTEXT
    })
