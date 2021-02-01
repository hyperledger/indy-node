import pytest

from indy_common.constants import RS_ID, GET_RICH_SCHEMA_OBJECT_BY_ID, RS_VERSION, RS_NAME, RS_CONTENT, RS_TYPE
from indy_common.types import Request
from indy_node.server.request_handlers.read_req_handlers.rich_schema.get_rich_schema_object_by_id_handler import \
    GetRichSchemaObjectByIdHandler
from indy_node.test.state_proof.helper import check_valid_proof
from indy_node.test.state_proof.test_state_multi_proofs_for_get_requests import is_proof_verified, save_multi_sig
from plenum.common.constants import TXN_TYPE, OP_VER, DATA, CURRENT_PROTOCOL_VERSION
from plenum.common.txn_util import reqToTxn, append_txn_metadata, get_payload_data
from plenum.common.util import randomString, SortedDict


@pytest.fixture()
def id():
    return randomString()


@pytest.fixture()
def get_rich_schema_req(id):
    return Request(identifier=randomString(),
                   reqId=1234,
                   sig="sig",
                   protocolVersion=CURRENT_PROTOCOL_VERSION,
                   operation={
                       TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_ID,
                       RS_ID: id,
                   })


@pytest.fixture()
def get_rich_schema_by_id_handler(db_manager):
    return GetRichSchemaObjectByIdHandler(db_manager)


@pytest.mark.request_handlers
def test_get_rich_schema_obj(db_manager, handler_and_request, id,
                             get_rich_schema_by_id_handler, get_rich_schema_req):
    # prepare: store object in state with bls multi-sg
    handler, request = handler_and_request
    op = request.operation
    op[RS_ID] = id
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(request)
    append_txn_metadata(txn, seq_no, txn_time)
    handler.update_state(txn, None, request)
    handler.state.commit()
    save_multi_sig(db_manager)

    # execute: get object
    result = get_rich_schema_by_id_handler.get_result(get_rich_schema_req)

    # check
    assert result
    expected_data = SortedDict({
        'ver': op[OP_VER],
        'id': op[RS_ID],
        'rsType': op[RS_TYPE],
        'rsName': op[RS_NAME],
        'rsVersion': op[RS_VERSION],
        'content': op[RS_CONTENT],
        'from': request.identifier,
        'endorser': request.endorser,
    })
    assert SortedDict(result['data']) == expected_data
    assert result['seqNo'] == seq_no
    assert result['txnTime'] == txn_time
    assert result['state_proof']
    check_valid_proof(result)
    path = id.encode()
    assert is_proof_verified(db_manager,
                             result['state_proof'],
                             path, result[DATA], seq_no, txn_time)


@pytest.mark.request_handlers
def test_get_rich_schema_obj_not_existent(db_manager, handler_and_request,
                                          get_rich_schema_by_id_handler, get_rich_schema_req):
    save_multi_sig(db_manager)

    # execute: get object
    result = get_rich_schema_by_id_handler.get_result(get_rich_schema_req)

    # check
    assert result
    assert result['data'] is None
    assert result['seqNo'] is None
    assert result['txnTime'] is None
    assert result['state_proof']
    check_valid_proof(result)


@pytest.mark.request_handlers
def test_get_rich_schema_obj_committed_only(db_manager, handler_and_request, id,
                                            get_rich_schema_by_id_handler, get_rich_schema_req):
    # prepare: store object in state with bls multi-sig, and then update the object (uncommitted)
    handler, request = handler_and_request
    op = request.operation
    op[RS_ID] = id
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(request)
    append_txn_metadata(txn, seq_no, txn_time)
    handler.update_state(txn, None, request)
    handler.state.commit()

    get_payload_data(txn)[RS_NAME] = "new uncommitted name"
    get_payload_data(txn)[RS_VERSION] = "3.0"
    handler.update_state(txn, None, request)

    save_multi_sig(db_manager)

    # execute: get object
    result = get_rich_schema_by_id_handler.get_result(get_rich_schema_req)

    # check
    assert result
    expected_data = SortedDict({
        'ver': op[OP_VER],
        'id': op[RS_ID],
        'rsType': op[RS_TYPE],
        'rsName': op[RS_NAME],
        'rsVersion': op[RS_VERSION],
        'content': op[RS_CONTENT],
        'from': request.identifier,
        'endorser': request.endorser,
    })
    assert SortedDict(result['data']) == expected_data
    assert result['seqNo'] == seq_no
    assert result['txnTime'] == txn_time
    assert result['state_proof']
    check_valid_proof(result)
    path = id.encode()
    assert is_proof_verified(db_manager,
                             result['state_proof'],
                             path, result[DATA], seq_no, txn_time)
