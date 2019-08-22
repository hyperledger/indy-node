import pytest
from plenum.common.constants import DATA, META

from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.constants import CONTEXT_NAME, CONTEXT_VERSION, CONTEXT_CONTEXT, RS_TYPE, CONTEXT_TYPE
from indy_node.test.context.helper import W3C_BASE_CONTEXT, SCHEMA_ORG_CONTEXT
from indy_common.types import SetContextMetaField
from indy_node.test.api.helper import validate_write_reply, sdk_write_context_and_check
from plenum.common.exceptions import RequestRejectedException
from plenum.common.util import randomString
from plenum.config import NAME_FIELD_LIMIT
import pickle
import sys


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
    x = sys.getsizeof(pickle.dumps(SCHEMA_ORG_CONTEXT))
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
    rep = sdk_write_context_and_check(
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
        x = len(SCHEMA_ORG_CONTEXT)
        validate_write_reply(resp)

