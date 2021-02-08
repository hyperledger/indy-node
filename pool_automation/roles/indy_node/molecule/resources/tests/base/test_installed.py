import pytest


@pytest.fixture(scope="module")
def ansible_vars(host):
    return host.ansible.get_variables()


def test_correct_package_versions_are_installed(host, ansible_vars):
    indy_node = host.package('indy-node')
    indy_plenum = host.package('indy-plenum')

    assert indy_node.is_installed
    assert indy_plenum.is_installed

    assert indy_node.version == ansible_vars['indy_node_ver']
    assert indy_plenum.version == ansible_vars['indy_plenum_ver']


def test_node_service_is_enabled(host):
    assert host.service('indy-node').is_enabled
