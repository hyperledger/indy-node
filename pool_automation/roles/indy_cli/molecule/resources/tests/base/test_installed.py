testinfra_hosts = ['clients']

def test_correct_package_versions_are_installed(host):
    v = host.ansible.get_variables()

    indy_cli = host.package('indy-cli')

    assert indy_cli.is_installed
    assert indy_cli.version == v['indy_cli_ver']

def test_indy_cli_is_available_in_path(host):
    assert host.exists('indy-cli')
