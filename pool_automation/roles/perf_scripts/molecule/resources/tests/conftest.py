import pytest


@pytest.fixture(scope="module")
def ansible_vars(host):
    return host.ansible.get_variables()


@pytest.fixture(scope="module")
def venv_path(host, ansible_vars):
    return "{}/{}".format(
        host.user().home,
        ansible_vars['perf_scripts_venv_name'])


@pytest.fixture(scope="module")
def pool_txns_path(host, ansible_vars):
    return "{}/{}".format(
        host.user().home,
        ansible_vars['perf_scripts_pool_genesis_txns_name'])
