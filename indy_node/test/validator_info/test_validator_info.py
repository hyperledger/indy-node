import pytest

import importlib

from stp_core.loop.eventually import eventually

from plenum.common.constants import TARGET_NYM, RAW, NAME, VERSION, ORIGIN
from plenum.test import waits
from plenum.test.helper import check_sufficient_replies_received


# noinspection PyUnresolvedReferences
from plenum.test.validator_info.test_validator_info import patched_dump_info_period, \
    info_path, info, load_info, load_latest_info, node  # qa

from indy_common.constants import TXN_TYPE, DATA, GET_NYM, GET_ATTR, GET_SCHEMA, GET_CLAIM_DEF, REF, SIGNATURE_TYPE

from indy_client.client.wallet.attribute import Attribute
from indy_node.__metadata__ import __version__ as node_pgk_version


TEST_NODE_NAME = 'Alpha'
STATUS_FILENAME = '{}_info.json'.format(TEST_NODE_NAME.lower())


def test_validator_info_file_schema_is_valid(info):
    assert isinstance(info, dict)
    assert 'config' in info['metrics']['transaction-count']
    assert 'software' in info
    assert 'indy-node' in info['software']
    assert 'sovrin' in info['software']


def test_validator_info_file_metrics_count_ledger_field_valid(info):
    assert info['metrics']['transaction-count']['config'] == 0


def test_validator_info_file_software_indy_node_valid(info):
    assert info['software']['indy-node'] == node_pgk_version


def test_validator_info_file_software_sovrin_valid(info):
    try:
        pkg = importlib.import_module('sovrin')
    except ImportError:
        assert info['software']['sovrin'] is None
    else:
        assert info['software']['sovrin'] == pkg.__version__


@pytest.fixture()
def node_with_broken_info_tool(node):
    node_bk = node._info_tool._node
    node._info_tool._node = None
    yield
    node._info_tool._node = node_bk


def test_validator_info_file_handle_fails(info,
                                          node_with_broken_info_tool,
                                          load_latest_info):
    latest_info = load_latest_info()

    assert latest_info['metrics']['transaction-count']['config'] is None


def test_validator_info_file_get_nym(info,
                                     read_txn_and_get_latest_info,
                                     reset_node_total_read_request_number,
                                     node):
    assert info['metrics']['average-per-second']['read-transactions'] == 0
    latest_info = read_txn_and_get_latest_info(GET_NYM)
    assert latest_info['metrics']['average-per-second']['read-transactions'] > 0


def test_validator_info_file_get_schema(info,
                                        read_txn_and_get_latest_info,
                                        reset_node_total_read_request_number,
                                        node):
    assert info['metrics']['average-per-second']['read-transactions'] == 0
    latest_info = read_txn_and_get_latest_info(GET_SCHEMA)
    assert latest_info['metrics']['average-per-second']['read-transactions'] > 0


def test_validator_info_file_get_attr(info,
                                      read_txn_and_get_latest_info,
                                      reset_node_total_read_request_number,
                                      node):
    assert info['metrics']['average-per-second']['read-transactions'] == 0
    latest_info = read_txn_and_get_latest_info(GET_ATTR)
    assert latest_info['metrics']['average-per-second']['read-transactions'] > 0


def test_validator_info_file_get_claim_def(info,
                                           read_txn_and_get_latest_info,
                                           reset_node_total_read_request_number,
                                           node):
    assert info['metrics']['average-per-second']['read-transactions'] == 0
    latest_info = read_txn_and_get_latest_info(GET_CLAIM_DEF)
    assert latest_info['metrics']['average-per-second']['read-transactions'] > 0


@pytest.fixture()
def client_and_wallet(steward, stewardWallet):
    return steward, stewardWallet


def submitRequests(client, wallet, op):
    req = wallet.signOp(op)
    # TODO: This looks boilerplate
    wallet.pendRequest(req)
    reqs = wallet.preparePending()
    return client.submitReqs(*reqs)[0]


def makeGetNymRequest(client, wallet, nym):
    op = {
        TARGET_NYM: nym,
        TXN_TYPE: GET_NYM,
    }
    return submitRequests(client, wallet, op)


def makeGetSchemaRequest(client, wallet, nym):
    op = {
        TARGET_NYM: nym,
        TXN_TYPE: GET_SCHEMA,
        DATA: {
            NAME: 'foo',
            VERSION: '1.0',
        }
    }
    return submitRequests(client, wallet, op)


def makeGetAttrRequest(client, wallet, nym, raw):
    op = {
        TARGET_NYM: nym,
        TXN_TYPE: GET_ATTR,
        RAW: raw
    }
    return submitRequests(client, wallet, op)


def makeGetClaimDefRequest(client, wallet):
    op = {
        TXN_TYPE: GET_CLAIM_DEF,
        ORIGIN: '1' * 16, # must be a valid DID
        REF: 1,
        SIGNATURE_TYPE: 'any'
    }
    return submitRequests(client, wallet, op)


@pytest.fixture
def read_txn_and_get_latest_info(txnPoolNodesLooper, patched_dump_info_period,
                                 client_and_wallet, info_path):
    client, wallet = client_and_wallet

    def read_wrapped(txn_type):

        if txn_type == GET_NYM:
            reqs = makeGetNymRequest(client, wallet, wallet.defaultId)
        elif txn_type == GET_SCHEMA:
            reqs = makeGetSchemaRequest(client, wallet, wallet.defaultId)
        elif txn_type == GET_ATTR:
            reqs = makeGetAttrRequest(client, wallet, wallet.defaultId, "attrName")
        elif txn_type == GET_CLAIM_DEF:
            reqs = makeGetClaimDefRequest(client, wallet)
        else:
            assert False, "unexpected txn type {}".format(txn_type)

        timeout = waits.expectedTransactionExecutionTime(
            len(client.inBox))
        txnPoolNodesLooper.run(
            eventually(check_sufficient_replies_received,
                       client, reqs[0].identifier, reqs[0].reqId,
                       retryWait=1, timeout=timeout))
        txnPoolNodesLooper.runFor(patched_dump_info_period)
        return load_info(info_path)
    return read_wrapped


@pytest.fixture
def reset_node_total_read_request_number(node):
    node.total_read_request_number = 0
