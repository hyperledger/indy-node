import pytest
from indy_node.utils.node_control_utils import NodeControlUtil


@pytest.mark.parametrize("vers_str,vers_parsed",
                         [("aa (= 1)", ["aa=1"]), ("aa (= 1), bb", ["aa=1", "bb"]),
                          ("aa (= 1), bb (= 2) | cc (= 3)", ["aa=1", "bb=2", "cc=3"]),
                          ("aa (< 1), bb (> 2) | cc (<= 3), dd (>= 4)", ["aa=1", "bb=2", "cc=3", "dd=4"]),
                          ("aa (<< 1), bb (>> 2) | cc (<= 3) | dd", ["aa=1", "bb=2", "cc=3", "dd"])])
def test_version_parse(vers_str, vers_parsed):
    vers = NodeControlUtil._parse_deps(vers_str)
    assert vers == vers_parsed


@pytest.mark.parametrize("pkcts,pkcts_dd",
                         [([], []), (["aa=1"], ["aa=1"]), (["aa=1", "aa=1", "aa=2"], ["aa=1"]),
                          (["aa=1", "bb=2", "cc=3"], ["aa=1", "bb=2", "cc=3"]),
                          (["aa=1", "bb=2", "cc=3", "aa=2", "bb=3", "cc=4"], ["aa=1", "bb=2", "cc=3"])])
def test_pkts_dedup(pkcts, pkcts_dd):
    processed_pckts = NodeControlUtil._pkts_dedup(pkcts)
    assert processed_pckts == pkcts_dd
