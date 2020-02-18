import pytest
from indy_common.authorize.auth_constraints import AuthConstraintForbidden
from indy_common.constants import RS_META, RS_DATA
from indy_node.server.request_handlers.domain_req_handlers.rich_schema.rs_schema_handler import RsSchemaHandler
from indy_node.test.request_handlers.helper import add_to_idr
from plenum.common.constants import TRUSTEE, TXN_PAYLOAD
from plenum.common.exceptions import UnauthorizedClientRequest
from plenum.common.txn_util import append_txn_metadata, reqToTxn

def test_static_validation_pass_context_w3c_examples_v1(context_operation):
    # test for https://www.w3.org/2018/credentials/examples/v1
    context_operation[RS_CONTENT] = json.dumps(W3C_EXAMPLE_V1_CONTEXT)
    req = Request("test", 1, context_operation, "sig", )
    ch = JsonLdContextHandler(None, None)
    ch.static_validation(req)