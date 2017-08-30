import importlib

from sovrin_node.__metadata__ import __version__ as node_pgk_version
# noinspection PyUnresolvedReferences
from plenum.test.validator_info.test_validator_info import patched_dump_info_period, \
    info_path, info, load_latest_info, node  # qa


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


def test_validator_info_file_handle_fails(info,
                                          node,
                                          load_latest_info):
    node._info_tool._node = None
    latest_info = load_latest_info()

    assert latest_info['metrics']['transaction-count']['config'] is None
