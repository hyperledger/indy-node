import pytest


@pytest.fixture(scope="module")
def ansible_vars(host):
    return host.ansible.get_variables()


def test_apt_https_is_installed(host):
    for pack in ['apt-transport-https', 'ca-certificates']:
        assert host.package(pack).is_installed


def test_keys_are_added(host):
    assert host.run(
        "apt-key adv --list-sigs --keyid-format LONG | grep {}"
        .format('repo@sovrin.org')).rc == 0


def test_node_repos_are_added(host, ansible_vars):
    for comp in ansible_vars['indy_repo_node_channels'].split():
        assert host.run(
            "apt-cache policy | grep '{} xenial/{}'"
            .format('https://repo.sovrin.org/deb', comp)).rc == 0


def test_sdk_repos_are_added(host, ansible_vars):
    for comp in ansible_vars['indy_repo_sdk_channels'].split():
        assert host.run(
            "apt-cache policy | grep '{} xenial/{}'"
            .format('https://repo.sovrin.org/sdk/deb', comp)).rc == 0
