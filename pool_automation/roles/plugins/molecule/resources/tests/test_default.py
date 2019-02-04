import pytest


@pytest.fixture(scope="module")
def ansible_vars(host):
    return host.ansible.get_variables()


def test_plugins_role_was_executed(host, ansible_vars):
    assert host.file(ansible_vars['plugins_test_file_path']).exists


def test_correct_plugins_are_installed(host, ansible_vars):
    for pack in ansible_vars['plugins_packages']:
        pack_spec = pack.split('=')  # TODO test fuzzy constraints
        assert host.package(pack_spec[0]).is_installed
        try:
            assert host.package(pack_spec[0]).version == pack_spec[1]
        except IndexError:
            pass
