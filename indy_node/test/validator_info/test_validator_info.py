import pytest

from indy_node.test.state_proof.helper import sdk_submit_operation_and_get_result
from plenum.common.constants import TARGET_NYM, RAW, NAME, VERSION, ORIGIN

# noinspection PyUnresolvedReferences
from plenum.common.ledger import Ledger
from plenum.test.primary_selection.test_primary_selector import FakeLedger
from plenum.test.validator_info.conftest import info, node  # qa

from indy_common.constants import TXN_TYPE, DATA, GET_NYM, GET_ATTR, GET_SCHEMA, GET_CLAIM_DEF, REF, SIGNATURE_TYPE
from indy_node.__metadata__ import __version__ as node_pgk_version

PERIOD_SEC = 1
TEST_NODE_NAME = 'Alpha'
STATUS_FILENAME = '{}_info.json'.format(TEST_NODE_NAME.lower())
INFO_FILENAME = '{}_info.json'.format(TEST_NODE_NAME.lower())


def test_validator_info_file_schema_is_valid(info):
    assert isinstance(info, dict)
    assert 'config' in info['Node_info']['Metrics']['transaction-count']


def test_validator_info_file_metrics_count_ledger_field_valid(info):
    assert info['Node_info']['Metrics']['transaction-count']['config'] == 0


def test_validator_info_bls_key_field_valid(node, info):
    assert info['Node_info']['BLS_key']


def test_validator_info_ha_fields_valid(node, info):
    assert info['Node_info']['Node_ip']
    assert info['Node_info']['Client_ip']
    assert info['Node_info']['Node_port']
    assert info['Node_info']['Client_port']


def test_validator_info_file_software_indy_node_valid(info):
    assert info['Software']['indy-node'] == node_pgk_version


@pytest.fixture()
def node_with_broken_info_tool(node):
    node_bk = node._info_tool._node
    node._info_tool._node = None
    yield
    node._info_tool._node = node_bk


def test_validator_info_file_handle_fails(node_with_broken_info_tool,
                                          node):
    latest_info = node._info_tool.info

    assert 'Node_info' not in latest_info


def test_validator_info_file_get_nym(read_txn_and_get_latest_info,
                                     node):
    reset_node_total_read_request_number(node)
    info = node._info_tool.info
    assert info['Node_info']['Metrics']['average-per-second']['read-transactions'] == 0
    latest_info = read_txn_and_get_latest_info(GET_NYM)
    assert latest_info['Node_info']['Metrics']['average-per-second']['read-transactions'] > 0


def test_validator_info_file_get_schema(read_txn_and_get_latest_info,
                                        node):
    reset_node_total_read_request_number(node)
    info = node._info_tool.info
    assert info['Node_info']['Metrics']['average-per-second']['read-transactions'] == 0
    latest_info = read_txn_and_get_latest_info(GET_SCHEMA)
    assert latest_info['Node_info']['Metrics']['average-per-second']['read-transactions'] > 0


def test_validator_info_file_get_attr(read_txn_and_get_latest_info,
                                      node):
    reset_node_total_read_request_number(node)
    info = node._info_tool.info
    assert info['Node_info']['Metrics']['average-per-second']['read-transactions'] == 0
    latest_info = read_txn_and_get_latest_info(GET_ATTR)
    assert latest_info['Node_info']['Metrics']['average-per-second']['read-transactions'] > 0


def test_validator_info_file_get_claim_def(read_txn_and_get_latest_info,
                                           node):
    reset_node_total_read_request_number(node)
    info = node._info_tool.info
    assert info['Node_info']['Metrics']['average-per-second']['read-transactions'] == 0
    latest_info = read_txn_and_get_latest_info(GET_CLAIM_DEF)
    assert latest_info['Node_info']['Metrics']['average-per-second']['read-transactions'] > 0


def makeGetNymRequest(looper, sdk_pool_handle, sdk_wallet, nym):
    op = {
        TARGET_NYM: nym,
        TXN_TYPE: GET_NYM,
    }
    return sdk_submit_operation_and_get_result(looper, sdk_pool_handle, sdk_wallet, op)


def makeGetSchemaRequest(looper, sdk_pool_handle, sdk_wallet, nym):
    op = {
        TARGET_NYM: nym,
        TXN_TYPE: GET_SCHEMA,
        DATA: {
            NAME: 'foo',
            VERSION: '1.0',
        }
    }
    return sdk_submit_operation_and_get_result(looper, sdk_pool_handle, sdk_wallet, op)


def makeGetAttrRequest(looper, sdk_pool_handle, sdk_wallet, nym, raw):
    op = {
        TARGET_NYM: nym,
        TXN_TYPE: GET_ATTR,
        RAW: raw
    }
    return sdk_submit_operation_and_get_result(looper, sdk_pool_handle, sdk_wallet, op)


def makeGetClaimDefRequest(looper, sdk_pool_handle, sdk_wallet):
    op = {
        TXN_TYPE: GET_CLAIM_DEF,
        ORIGIN: '1' * 16,  # must be a valid DID
        REF: 1,
        SIGNATURE_TYPE: 'any'
    }
    return sdk_submit_operation_and_get_result(looper, sdk_pool_handle, sdk_wallet, op)


@pytest.fixture
def read_txn_and_get_latest_info(looper, sdk_pool_handle,
                                 sdk_wallet_client, node):
    _, did = sdk_wallet_client

    def read_wrapped(txn_type):
        if txn_type == GET_NYM:
            makeGetNymRequest(looper, sdk_pool_handle, sdk_wallet_client, did)
        elif txn_type == GET_SCHEMA:
            makeGetSchemaRequest(looper, sdk_pool_handle, sdk_wallet_client, did)
        elif txn_type == GET_ATTR:
            makeGetAttrRequest(looper, sdk_pool_handle, sdk_wallet_client, did, "attrName")
        elif txn_type == GET_CLAIM_DEF:
            makeGetClaimDefRequest(looper, sdk_pool_handle, sdk_wallet_client)
        else:
            assert False, "unexpected txn type {}".format(txn_type)
        return node._info_tool.info

    return read_wrapped


def reset_node_total_read_request_number(node):
    node.total_read_request_number = 0


class FakeTree:
    @property
    def root_hash(self):
        return '222222222222222222222222222'

class FakeLedgerEx(FakeLedger):
    @property
    def uncommittedRootHash(self):
        return '111111111111111111111111111111111'

    @property
    def uncommittedTxns(self):
        return []

    @property
    def tree(self):
        return FakeTree()

    @property
    def size(self):
        return 100


def test_validator_info_file_metrics_count_all_ledgers_field_valid(node):
    new_ids = [444, 555, 666, 777]
    for newid in new_ids:
        node.ledgerManager.addLedger(newid, FakeLedgerEx(newid, newid))
    info = node._info_tool.info
    has_cnt = len(info['Node_info']['Metrics']['transaction-count'])
    assert has_cnt == len(new_ids) + 4


def test_validator_info_update_date_field_valid(info):
    assert "Update_time" in info
    import time
    import datetime
    from_str = time.mktime(datetime.datetime.strptime(info["Update_time"],
                                                      "%A, %B %d, %Y %I:%M:%S %p %z").timetuple())
    assert int(from_str) == info["timestamp"]
