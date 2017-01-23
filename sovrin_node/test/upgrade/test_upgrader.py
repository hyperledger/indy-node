# Some unit tests for upgrader
from sovrin_node.server.upgrader import Upgrader


def testVersions():
    assert Upgrader.getNumericValueOfVersion('12.3') > \
           Upgrader.getNumericValueOfVersion('1.23')
    assert Upgrader.getNumericValueOfVersion('1.22.3') > \
           Upgrader.getNumericValueOfVersion('1.2.23')
    assert Upgrader.isVersionHigher('0.0.5', '0.0.6')
    assert not Upgrader.isVersionHigher('0.0.9', '0.0.8')
    assert Upgrader.isVersionHigher('0.0.9', '0.1.0')
    assert Upgrader.isVersionHigher('1.0.0', '0.20.30')
