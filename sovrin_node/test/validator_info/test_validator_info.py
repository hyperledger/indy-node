# noinspection PyUnresolvedReferences
from plenum.test.validator_info.test_validator_info import patched_dump_info_period, \
    info_path, info  # qa


TEST_NODE_NAME = 'Alpha'
STATUS_FILENAME = '{}_info.json'.format(TEST_NODE_NAME.lower())


def test_validator_info_file_schema_is_valid(info):
    assert isinstance(info, dict)
    assert 'config' in info['metrics']['transaction-count']


def test_validator_info_file_metrics_count_ledger_field_valid(info):
    assert info['metrics']['transaction-count']['config'] == 0
