import pytest

testinfra_hosts = ['clients']


def test_venv_exists(host, venv_path):
    assert host.file(venv_path).exists
    assert host.file(venv_path).is_directory


def test_correct_packages_are_installed(host, ansible_vars):
    libindy = host.package('libindy')
    assert libindy.is_installed

    if ansible_vars['perf_scripts_libindy_ver'] is not None:
        assert libindy.version == ansible_vars['perf_scripts_libindy_ver']


def test_correct_python_packages_are_installed_inside_venv(host, ansible_vars, venv_path):
    pip_path = "{}/bin/pip".format(venv_path)

    pip_packages = host.pip_package.get_packages(pip_path=pip_path)

    # TODO version check for VCS as package source
    assert 'indy-perf-load' in pip_packages
    assert 'python3-indy' in pip_packages

    # TODO python3-indy's package metadata doesn't match package version
    # for non-stable packages, thus the check will fail for them
    if (ansible_vars['perf_scripts_python3_indy_ver'] is not None and
            'dev' not in ansible_vars['perf_scripts_python3_indy_ver']):
        assert pip_packages['python3-indy']['version'] == ansible_vars['perf_scripts_python3_indy_ver']


def test_perf_processes_is_runable(host, venv_path):
    assert host.run("{}/bin/perf_processes.py --help".format(venv_path)).rc == 0


def test_perf_spike_load_is_runable(host, venv_path):
    assert host.run("{}/bin/perf_spike_load.py --help".format(venv_path)).rc == 0
