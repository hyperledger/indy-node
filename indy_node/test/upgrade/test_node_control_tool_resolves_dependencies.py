from indy_node.utils.node_control_tool import NodeControlTool
from plenum.test.helper import randomText
from indy_node.utils.node_control_utils import NodeControlUtil, MAX_DEPS_DEPTH


def testNodeControlResolvesDependencies(monkeypatch, tconf):
    nct = NodeControlTool(config=tconf)
    node_package = ('indy-node', '0.0.1')
    plenum_package = ('indy-plenum', '0.0.3')
    node_package_with_version = '{}={}'.format(*node_package)
    plenum_package_with_version = '{}={}'.format(*plenum_package)
    mock_info = {node_package_with_version: '{}\nVersion: {}\nDepends:{} (= {})\n'.format(
        randomText(100), node_package[1], *plenum_package),
        plenum_package_with_version: '{}'.format(randomText(100))
    }

    def mock_get_info_from_package_manager(*package):
        ret = ""
        for p in package:
            ret += mock_info.get(p, "")
        return ret

    monkeypatch.setattr(NodeControlUtil, 'update_package_cache', lambda *x: None)
    monkeypatch.setattr(NodeControlUtil, 'get_sys_holds',
                        lambda *x: [node_package[0], plenum_package[0]])
    monkeypatch.setattr(NodeControlUtil, '_get_info_from_package_manager',
                        lambda *x: mock_get_info_from_package_manager(*x))
    ret = nct._get_deps_list(node_package_with_version)
    nct.server.close()
    assert sorted(ret.split()) == sorted([plenum_package_with_version,
                                          node_package_with_version])


def test_create_deps_for_exotic_version_style():
    depends = ['package1', 'package2']
    versions = ['1.6.74', '0.9.4~+.-AbCd1.2.3.4.EiF']
    def mock_info_from_package_manager(*package):
        pkg_info = """Package: {package}
Version: 1.1.26
Priority: extra
Section: default
Maintainer: Some Organization <some_org@org.com>
Installed-Size: 21.5 kB
Depends: {dep1} (= {ver1}), {dep2} (= {ver2})
Homepage: https://github.com/some/package
License: Apache 2.0
Vendor: none
Download-Size: 10.4 kB
APT-Sources: https://some.org/deb xenial/rc amd64 Packages
Description: Some package
""".format(**{'package': package[0],
            'dep1': depends[0],
            'dep2': depends[1],
            'ver1': versions[0],
            'ver2': versions[1]})
        return pkg_info
    ncu = NodeControlUtil
    ncu._get_info_from_package_manager = mock_info_from_package_manager
    ret = ncu.get_deps_tree('package', depth=MAX_DEPS_DEPTH-1)
    """
    Expected return value is:
    0 item is package,
    1 deps with version for previous package,
    """
    assert len(ret[1][0]) == len(depends)
    assert any([depends[0] in l for l in ret[1][0]])
    assert any([depends[0] in l for l in ret[1][0]])
    assert any(["{}={}".format(depends[0], versions[0]) in l for l in ret[1][0]])
    assert any(["{}={}".format(depends[1], versions[1]) in l for l in ret[1][0]])


def test_max_depth_for_deps_tree():
    depends = ['package1', 'package2']
    def mock_info_from_package_manager(*package):
        pkg_info = """Depends: {} (= 1.1.1), {} (= 2.2.2)""".format(depends[0],
                                                                    depends[1])
        return pkg_info

    ncu = NodeControlUtil
    ncu._get_info_from_package_manager = mock_info_from_package_manager
    ret = ncu.get_deps_tree('package')
    assert len(ret) <= MAX_DEPS_DEPTH