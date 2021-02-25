
def test_python_is_installed(host):
    assert host.run('python --version').rc == 0
