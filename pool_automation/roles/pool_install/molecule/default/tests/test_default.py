
def test_node_is_configured_correctly(host):
    indy_config = host.file('/etc/indy/indy_config.py')
    assert indy_config.exists
    assert indy_config.user == 'indy'
    assert indy_config.group == 'indy'
    assert indy_config.contains("NETWORK_NAME = 'sandbox'")


def test_node_service_is_running(host):
    node_svc = host.service('indy-node')
    assert node_svc.is_enabled
    assert node_svc.is_running
