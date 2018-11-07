
def test_python_is_installed(host):
    assert host.run('python --version').rc == 0


def test_sudo_is_installed(host):
    assert host.run('sudo --version').rc == 0
