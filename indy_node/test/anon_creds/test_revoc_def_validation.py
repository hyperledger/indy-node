import pytest

from indy_common.constants import CRED_DEF_ID
from indy_common.types import Request
from plenum.common.constants import DOMAIN_LEDGER_ID
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.util import randomString


def test_validation_cred_def_not_present(build_revoc_def_by_default,
                                         create_node_and_not_start):
    node = create_node_and_not_start
    req = build_revoc_def_by_default
    with pytest.raises(InvalidClientRequest, match="There is no any CRED_DEF"):
        node.write_manager.dynamic_validation(Request(**req), 0)


def test_invalid_cred_def_id_format(build_revoc_def_by_default,
                                    create_node_and_not_start):
    node = create_node_and_not_start
    req = build_revoc_def_by_default

    req['operation'][CRED_DEF_ID] = ":".join(3 * [randomString(10)])
    with pytest.raises(InvalidClientRequest, match="Format of {} field is not acceptable".format(CRED_DEF_ID)):
        node.write_manager.static_validation(Request(**req))

    req['operation'][CRED_DEF_ID] = ":".join(6 * [randomString(10)])
    with pytest.raises(InvalidClientRequest, match="Format of {} field is not acceptable".format(CRED_DEF_ID)):
        node.write_manager.static_validation(Request(**req))
