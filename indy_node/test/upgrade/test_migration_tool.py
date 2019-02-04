import indy_node.utils.migration_tool as migration_tool
import pytest
from timeout_decorator import TimeoutError


TEST_MIGRATION_SCRIPTS = [
    '0_3_100_to_0_3_104',
    '10_2_1_to_10_0_2',
    '0_9_2_to_0_9_10',
    '0_3_100_to_0_3_101',
    '0_1_10_to_0_9_10',
    '0_3_4_invalid']
TEST_VERSION = '0.3.100'
TEST_NEW_VERSION = '0.10.105'
TEST_TIMEOUT = 1


def testGetRelevantMigrations():
    relevantMigrations = migration_tool._get_relevant_migrations(
        TEST_MIGRATION_SCRIPTS, TEST_VERSION, TEST_NEW_VERSION)
    assert len(relevantMigrations) == 3
    assert relevantMigrations == [
        '0_3_100_to_0_3_101', '0_3_100_to_0_3_104', '0_9_2_to_0_9_10']


def testMigrate(monkeypatch):
    testList = []

    monkeypatch.setattr(migration_tool, '_call_migration_script',
                        lambda *x: testList.append(x[0]))
    monkeypatch.setattr(migration_tool, '_get_migration_scripts',
                        lambda *x: TEST_MIGRATION_SCRIPTS)

    assert migration_tool.migrate(
        TEST_VERSION, TEST_NEW_VERSION, TEST_TIMEOUT) == 3
    assert len(testList) == 3


def testMigrateTimesOut(monkeypatch):
    monkeypatch.setattr(migration_tool, '_call_migration_script',
                        lambda *x: exec('raise(TimeoutError())'))
    monkeypatch.setattr(migration_tool, '_get_migration_scripts',
                        lambda *x: TEST_MIGRATION_SCRIPTS)

    with pytest.raises(TimeoutError):
        migration_tool.migrate(TEST_VERSION, TEST_NEW_VERSION, TEST_TIMEOUT)

def testGetMigrationScripts():
    try:
        res = migration_tool._get_migration_scripts(migration_tool._get_current_platform())
    except Exception as e:
        pytest.fail("Unexpected error: {}".format(e))
    else:
        assert type(res) is list
        assert res
