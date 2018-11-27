import pytest


@pytest.fixture(scope="module")
def venv_path(host):
    return "{}/{}".format(
        host.user().home,
        host.ansible.get_variables()['perf_scripts_venv_name'])


@pytest.fixture(scope="module")
def pool_txns_path(host):
    return "{}/{}".format(
        host.user().home,
        host.ansible.get_variables()['perf_scripts_pool_genesis_txns_name'])
