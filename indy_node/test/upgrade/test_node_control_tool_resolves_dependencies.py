from indy_node.utils.node_control_tool import NodeControlTool
from plenum.test.helper import randomText
from indy_node.utils.node_control_utils import NodeControlUtil


def testNodeControlResolvesDependencies(monkeypatch, tconf):
    nct = NodeControlTool(config=tconf)
    node_package = ('indy-node', '0.0.1')
    anoncreds_package = ('indy-anoncreds', '0.0.2')
    plenum_package = ('indy-plenum', '0.0.3')
    node_package_with_version = '{}={}'.format(*node_package)
    plenum_package_with_version = '{}={}'.format(*plenum_package)
    anoncreds_package_with_version = '{}={}'.format(*anoncreds_package)
    mock_info = {node_package_with_version: '{}{} (= {}){}{} (= {}){}'.format(
        randomText(100), *plenum_package, randomText(100), *anoncreds_package, randomText(100)),
        plenum_package_with_version: '{}'.format(randomText(100)),
        anoncreds_package_with_version: '{}'.format(randomText(100))
    }

    def mock_get_info_from_package_manager(package):
        return mock_info.get(package, None)

    monkeypatch.setattr(NodeControlUtil, 'update_package_cache', lambda *x: None)
    monkeypatch.setattr(NodeControlUtil, '_get_info_from_package_manager',
                        lambda x: mock_get_info_from_package_manager(x))
    ret = nct._get_deps_list(node_package_with_version)
    nct.server.close()
    assert ret.split() == [anoncreds_package_with_version, plenum_package_with_version, node_package_with_version]