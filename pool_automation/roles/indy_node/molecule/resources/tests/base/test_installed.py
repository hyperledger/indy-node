
def test_correct_package_versions_are_installed(host):
    v = host.ansible.get_variables()

    indy_node = host.package('indy-node')
    indy_plenum = host.package('indy-plenum')
    python_indy_crypto = host.package('python3-indy-crypto')
    libindy_crypto = host.package('libindy-crypto')

    assert indy_node.is_installed
    assert indy_plenum.is_installed
    assert python_indy_crypto.is_installed
    assert libindy_crypto.is_installed

    assert indy_node.version == v['indy_node_ver']
    assert indy_plenum.version == v['indy_plenum_ver']
    assert python_indy_crypto.version == v['python_indy_crypto_ver']
    assert libindy_crypto.version == v['libindy_crypto_ver']


def test_correct_add_packages_are_installed(host):
    v = host.ansible.get_variables()

    for pack in v['indy_node_add_packages']:
        pack_spec = pack.split('=') # TODO test fuzzy constraints
        assert host.package(pack_spec[0]).is_installed
        try:
            assert host.package(pack_spec[0]).version == pack_spec[1]
        except IndexError:
            pass


def test_node_service_is_enabled(host):
    assert host.service('indy-node').is_enabled
