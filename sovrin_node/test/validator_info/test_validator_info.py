# noinspection PyUnresolvedReferences
from plenum.test.validator_info.test_validator_info import patched_dump_info_period, \
    info_path, info, load_latest_info, node  # qa


TEST_NODE_NAME = 'Alpha'
STATUS_FILENAME = '{}_info.json'.format(TEST_NODE_NAME.lower())


def test_validator_info_file_schema_is_valid(info):
    assert isinstance(info, dict)
    assert 'config' in info['metrics']['transaction-count']


def test_validator_info_file_metrics_count_ledger_field_valid(info):
    assert info['metrics']['transaction-count']['config'] == 0


def test_validator_info_file_handle_fails(info,
                                          node,
                                          load_latest_info):
    node._info_tool._node = None
    latest_info = load_latest_info()

    assert latest_info['metrics']['transaction-count']['config'] is None
