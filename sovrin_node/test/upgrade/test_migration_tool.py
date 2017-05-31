import migration_tool


TEST_MIGRATION_SCRIPTS = ['0_3_100_0_test', '10_2_1_test1', '0_9_2_test3', '0_3_100_1_test4', '0_1_10_2_test5']
TEST_VERSION = '0.3.100'


def testGetRelevantMigrations():
    relevantMigrations = migration_tool._get_relevant_migrations(TEST_MIGRATION_SCRIPTS, TEST_VERSION)
    assert len(relevantMigrations) == 4
    assert relevantMigrations == ['0_3_100_0_test', '0_3_100_1_test4', '0_9_2_test3', '10_2_1_test1']


def testMigrate(monkeypatch):
    testList = []

    monkeypatch.setattr(migration_tool, '_call_migration_script', testList.append)
    monkeypatch.setattr(migration_tool, '_get_migration_scripts', lambda: TEST_MIGRATION_SCRIPTS)

    assert migration_tool.migrate(TEST_VERSION) == 4
    assert len(testList) == 4


