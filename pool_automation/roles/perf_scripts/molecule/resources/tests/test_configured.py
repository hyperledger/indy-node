import pytest

testinfra_hosts = ['clients']


def test_pool_txns_genesis_file_exists(host, pool_txns_path):
    txns_file = host.file(pool_txns_path)
    assert txns_file.exists


def test_perf_processes_can_connect(host, venv_path, pool_txns_path):
    assert host.run(
        "{}/bin/perf_processes.py --test_conn -g {}"
        .format(venv_path, pool_txns_path)).rc == 0
