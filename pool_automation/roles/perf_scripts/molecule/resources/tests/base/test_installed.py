import pytest

testinfra_hosts = ['clients']


def test_venv_exists(host, venv_path):
    assert host.file(venv_path).exists
    assert host.file(venv_path).is_directory


def test_perf_load_package_is_installed_inside_venv(host, venv_path):
    pip_packages = host.pip_package.get_packages(
        pip_path="{}/bin/pip".format(venv_path))
    assert 'indy-perf-load' in pip_packages


def test_perf_processes_is_runable(host, venv_path):
    assert host.run("{}/bin/perf_processes.py --help".format(venv_path)).rc == 0


def test_perf_spike_load_is_runable(host, venv_path):
    assert host.run("{}/bin/perf_spike_load.py --help".format(venv_path)).rc == 0
