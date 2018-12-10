import pytest


@pytest.fixture(scope="module")
def ansible_vars(host):
    return host.ansible.get_variables()


def test_correct_package_versions_are_installed(host, ansible_vars):
    indy_node = host.package('indy-node')
    indy_plenum = host.package('indy-plenum')
    python_indy_crypto = host.package('python3-indy-crypto')
    libindy_crypto = host.package('libindy-crypto')

    assert indy_node.is_installed
    assert indy_plenum.is_installed
    assert python_indy_crypto.is_installed
    assert libindy_crypto.is_installed

    assert indy_node.version == ansible_vars['indy_node_ver']
    assert indy_plenum.version == ansible_vars['indy_plenum_ver']
    assert python_indy_crypto.version == ansible_vars['python_indy_crypto_ver']
    assert libindy_crypto.version == ansible_vars['libindy_crypto_ver']


def test_node_service_is_enabled(host):
    assert host.service('indy-node').is_enabled
