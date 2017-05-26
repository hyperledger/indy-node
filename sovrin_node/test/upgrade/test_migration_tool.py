import migration_tool


TEST_MIGRATION_SCRIPTS = ['0.3.100_0_test', '10.2.1_test1', '0.9.2_test3', '0.3.100_1_test4', '0.1.10_2_test5']
TEST_VERSION = '0.3.100'


def testGetRelevantMigrations():
    relevantMigrations = migration_tool._get_relevalnt_migrations(TEST_MIGRATION_SCRIPTS, TEST_VERSION)
    assert len(relevantMigrations) == 4
    print(relevantMigrations)
    assert relevantMigrations == ['0.3.100_0_test', '0.3.100_1_test4', '0.9.2_test3', '10.2.1_test1']


def testMigrate(monkeypatch):
    testList = []

    monkeypatch.setattr(migration_tool, '_call_migration_script', testList.append)
    monkeypatch.setattr(migration_tool, '_get_migration_scripts', lambda: TEST_MIGRATION_SCRIPTS)

    assert migration_tool.migrate(TEST_VERSION) == 4
    assert len(testList) == 4


