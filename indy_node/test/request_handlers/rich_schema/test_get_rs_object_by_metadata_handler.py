import pytest

from indy_common.constants import RS_ID, RS_VERSION, RS_NAME, RS_CONTENT, RS_TYPE, \
    GET_RICH_SCHEMA_OBJECT_BY_METADATA
from indy_common.types import Request
from indy_node.server.request_handlers.read_req_handlers.rich_schema.get_rich_schema_object_by_metadata_handler import \
    GetRichSchemaObjectByMetadataHandler
from indy_node.test.state_proof.helper import check_valid_proof
from indy_node.test.state_proof.test_state_multi_proofs_for_get_requests import is_proof_verified, save_multi_sig
from plenum.common.constants import TXN_TYPE, OP_VER, DATA, CURRENT_PROTOCOL_VERSION
from plenum.common.txn_util import reqToTxn, append_txn_metadata, get_payload_data
from plenum.common.util import randomString, SortedDict


@pytest.fixture()
def metadata():
    return randomString(), randomString(), randomString()


@pytest.fixture()
def get_rich_schema_req(metadata):
    return Request(identifier=randomString(),
                   reqId=1234,
                   sig="sig",
                   protocolVersion=CURRENT_PROTOCOL_VERSION,
                   operation={
                       TXN_TYPE: GET_RICH_SCHEMA_OBJECT_BY_METADATA,
                       RS_NAME: metadata[0],
                       RS_VERSION: metadata[1],
                       RS_TYPE: metadata[2]
                   })


@pytest.fixture()
def get_rich_schema_by_meta_handler(db_manager):
    return GetRichSchemaObjectByMetadataHandler(db_manager)


def test_get_rich_schema_obj(db_manager, handler_and_request, metadata,
                             get_rich_schema_by_meta_handler, get_rich_schema_req):
    # prepare: store object in state with bls multi-sg
    handler, request = handler_and_request
    rs_name, rs_version, rs_type = metadata
    op = request.operation
    op[RS_NAME] = rs_name
    op[RS_VERSION] = rs_version
    op[RS_TYPE] = rs_type
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(request)
    append_txn_metadata(txn, seq_no, txn_time)
    handler.update_state(txn, None, request)
    handler.state.commit()
    save_multi_sig(db_manager)

    # execute: get object
    result = get_rich_schema_by_meta_handler.get_result(get_rich_schema_req)

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
    path = op[RS_ID].encode()
    assert is_proof_verified(db_manager,
                             result['state_proof'],
                             path, result[DATA], seq_no, txn_time)


def test_get_rich_schema_obj_not_existent(db_manager, handler_and_request, metadata,
                                          get_rich_schema_by_meta_handler, get_rich_schema_req):
    save_multi_sig(db_manager)

    # execute: get object
    result = get_rich_schema_by_meta_handler.get_result(get_rich_schema_req)

    # check
    assert result
    assert result['data'] is None
    assert result['seqNo'] is None
    assert result['txnTime'] is None
    assert result['state_proof']
    check_valid_proof(result)


def test_get_rich_schema_obj_committed_only(db_manager, handler_and_request, metadata,
                                            get_rich_schema_by_meta_handler, get_rich_schema_req):
    # prepare: store object in state with bls multi-sig, and then update the object (uncommitted)
    handler, request = handler_and_request
    rs_name, rs_version, rs_type = metadata
    op = request.operation
    op[RS_NAME] = rs_name
    op[RS_VERSION] = rs_version
    op[RS_TYPE] = rs_type
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(request)
    append_txn_metadata(txn, seq_no, txn_time)
    handler.update_state(txn, None, request)
    handler.state.commit()

    get_payload_data(txn)[RS_CONTENT] = "new uncommitted content"
    handler.update_state(txn, None, request)

    save_multi_sig(db_manager)

    # execute: get object
    result = get_rich_schema_by_meta_handler.get_result(get_rich_schema_req)

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
    path = op[RS_ID].encode()
    assert is_proof_verified(db_manager,
                             result['state_proof'],
                             path, result[DATA], seq_no, txn_time)
