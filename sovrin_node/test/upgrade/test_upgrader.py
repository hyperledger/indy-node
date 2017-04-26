# Some unit tests for upgrader
from sovrin_node.server.upgrader import Upgrader


def testVersions():
    assert Upgrader.isVersionHigher('0.0.5', '0.0.6')
    assert not Upgrader.isVersionHigher('0.0.9', '0.0.8')
    assert Upgrader.isVersionHigher('0.0.9', '0.1.0')
    assert Upgrader.isVersionHigher('0.20.30', '1.0.0')
    assert Upgrader.isVersionHigher('1.3.19', '1.3.20')
    versions = ['0.0.1', '0.10.11', '0.0.10', '0.0.2',
                '1.9.0', '9.10.0', '9.1.0']
    assert Upgrader.versionsDescOrder(versions) == \
           ['9.10.0', '9.1.0', '1.9.0', '0.10.11', '0.0.10', '0.0.2', '0.0.1']
