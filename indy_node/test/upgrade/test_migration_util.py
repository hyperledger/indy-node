from indy_node.utils.migration_tool import _get_relevant_migrations


def comparator_relevant_migration_script(
        migration_scripts,
        current_version,
        new_version,
        expected_migration_scripts):
    assert expected_migration_scripts == _get_relevant_migrations(
        migration_scripts, current_version, new_version)


def test_relevant_migration_script_positive():
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '1.0.95',
                                         '1.0.98',
                                         ['1_0_96_to_1_0_97'])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '1.0.96',
                                         '1.0.97',
                                         ['1_0_96_to_1_0_97'])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '0.0.56',
                                         '1.0.97',
                                         ['1_0_96_to_1_0_97'])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '0.0.56',
                                         '2.0.97',
                                         ['1_0_96_to_1_0_97'])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '1.0.96',
                                         '2.0.1',
                                         ['1_0_96_to_1_0_97'])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '1.0.86',
                                         '1.0.100',
                                         ['1_0_96_to_1_0_97'])


def test_relevant_migration_script_current_version_higher():
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '1.0.97',
                                         '1.0.98',
                                         [])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '1.0.97',
                                         '1.0.97',
                                         [])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '1.0.100',
                                         '1.0.102',
                                         [])


def test_relevant_migration_script_downgrade():
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '1.0.97',
                                         '1.0.96',
                                         [])
    comparator_relevant_migration_script(['1_0_97_to_1_0_96'],
                                         '1.0.97',
                                         '1.0.96',
                                         ['1_0_97_to_1_0_96'])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97', '1_0_97_to_1_0_96'],
                                         '1.0.84',
                                         '1.0.102',
                                         ['1_0_96_to_1_0_97'])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97', '1_0_97_to_1_0_96'],
                                         '1.0.102',
                                         '1.0.84',
                                         ['1_0_97_to_1_0_96'])


def test_relevant_migration_script_new_version_lower():
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '1.0.87',
                                         '1.0.96',
                                         [])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '0.0.57',
                                         '0.0.197',
                                         [])


def test_relevant_migration_script_multiple_scripts():
    comparator_relevant_migration_script(['1_0_96_to_1_0_97', '1_0_100_to_1_0_102'],
                                         '1.0.87',
                                         '1.0.97',
                                         ['1_0_96_to_1_0_97'])
    comparator_relevant_migration_script(
        [
            '1_0_96_to_1_0_97', '1_0_100_to_1_0_102'], '1.0.87', '1.0.102', [
            '1_0_96_to_1_0_97', '1_0_100_to_1_0_102'])
    comparator_relevant_migration_script(
        [
            '1_0_96_to_1_0_97', '1_0_100_to_1_0_102'], '1.0.96', '1.0.102', [
            '1_0_96_to_1_0_97', '1_0_100_to_1_0_102'])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97', '1_0_100_to_1_0_102'],
                                         '1.0.98',
                                         '1.0.102',
                                         ['1_0_100_to_1_0_102'])
    comparator_relevant_migration_script(
        ['1_0_96_to_1_0_97', '1_0_100_to_1_0_102'], '1.0.103', '1.0.104', [])
    comparator_relevant_migration_script(
        ['1_0_96_to_1_0_97', '1_0_100_to_1_0_102'], '1.0.103', '1.0.104', [])
    comparator_relevant_migration_script(
        [
            '1_0_96_to_1_0_97', '1_0_96_to_1_0_102'], '1.0.87', '1.0.102', [
            '1_0_96_to_1_0_97', '1_0_96_to_1_0_102'])
    comparator_relevant_migration_script(
        [
            '1_0_96_to_1_0_97', '1_0_96_to_1_0_102', '1_0_98_to_1_0_102'], '1.0.87', '1.0.102', [
            '1_0_96_to_1_0_97', '1_0_96_to_1_0_102', '1_0_98_to_1_0_102'])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97',
                                          '1_0_97_to_1_0_102',
                                          '1_0_102_to_1_0_104'],
                                         '1.0.87',
                                         '1.0.104',
                                         ['1_0_96_to_1_0_97',
                                          '1_0_97_to_1_0_102',
                                          '1_0_102_to_1_0_104'])


def test_relevant_migration_reinstall():
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '1.0.96',
                                         '1.0.96',
                                         [])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '1.0.97',
                                         '1.0.97',
                                         [])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '1.0.100',
                                         '1.0.100',
                                         [])
    comparator_relevant_migration_script(['1_0_96_to_1_0_97'],
                                         '1.0.95',
                                         '1.0.95',
                                         [])
