import pytest
from indy_node.utils.node_control_utils import NodeControlUtil


# a -> bb, cc
# bb -> ddd
# cc -> eee
# ddd -> ffff, jjjj
# eee -> hhhh, iiii
pkg_a = ('a', '0.0.0')
pkg_bb = ('bb', '1.0.0')
pkg_cc = ('cc', '1.0.0')
pkg_ddd = ('ddd', '1.1.0')
pkg_eee = ('eee', '1.1.0')
pkg_ffff = ('ffff', '1.1.1')
pkg_jjjj = ('jjjj', '1.1.1')
pkg_hhhh = ('hhhh', '1.1.1')
pkg_iiii = ('iiii', '1.1.1')

mock_info = {
    "{}={}".format(*pkg_a): 'Version: {}\nDepends:{} (= {}), {} (= {})\n'.format(pkg_a[1], *pkg_bb, *pkg_cc),
    "{}={}".format(*pkg_bb): 'Version: {}\nDepends:{} (= {})\n'.format(pkg_bb[1], *pkg_ddd),
    "{}={}".format(*pkg_cc): 'Version: {}\nDepends:{} (= {})\n'.format(pkg_cc[1], *pkg_eee),
    "{}={}".format(*pkg_ddd): 'Version: {}\nDepends:{} (= {}), {} (= {})\n'.format(pkg_ddd[1], *pkg_ffff, *pkg_jjjj),
    "{}={}".format(*pkg_eee): 'Version: {}\nDepends:{} (= {}), {} (= {})\n'.format(pkg_eee[1], *pkg_hhhh, *pkg_iiii),
    "{}={}".format(*pkg_ffff): 'Version: {}\nDepends: \n'.format(pkg_ffff[1]),
    "{}={}".format(*pkg_jjjj): 'Version: {}\nDepends: \n'.format(pkg_jjjj[1]),
    "{}={}".format(*pkg_hhhh): 'Version: {}\nDepends: \n'.format(pkg_hhhh[1]),
    "{}={}".format(*pkg_iiii): 'Version: {}\nDepends: \n'.format(pkg_iiii[1])
}


def mock_get_info_from_package_manager(*package):
    ret = ""
    for p in package:
        ret += mock_info.get(p, "")
    return ret


@pytest.fixture()
def patch_pkg_mgr(monkeypatch):
    monkeypatch.setattr(NodeControlUtil, '_get_info_from_package_manager',
                        lambda *x: mock_get_info_from_package_manager(*x))


@pytest.mark.parametrize("fltr_hld,res_dep",
                         [([], [pkg_a]),
                          ([pkg_a[0]], [pkg_a]),
                          ([pkg_a[0], pkg_cc[0]], [pkg_a, pkg_bb, pkg_cc]),
                          ([pkg_cc[0]], [pkg_a, pkg_bb, pkg_cc]),
                          ([pkg_a[0], pkg_cc[0], pkg_ddd[0]], [pkg_a, pkg_bb, pkg_cc, pkg_ddd, pkg_eee]),
                          (["out_scope"], [pkg_a, pkg_bb, pkg_cc, pkg_ddd, pkg_eee, pkg_iiii, pkg_hhhh, pkg_jjjj, pkg_ffff]),
                          ])
def test_deps_levels(patch_pkg_mgr, fltr_hld, res_dep):
    deps_list = NodeControlUtil.get_deps_tree_filtered('{}={}'.format(*pkg_a), filter_list=fltr_hld)
    flat_deps = []
    NodeControlUtil.dep_tree_traverse(deps_list, flat_deps)
    assert len(flat_deps) == len(res_dep)
    for d in res_dep:
        assert "{}={}".format(*d) in flat_deps
