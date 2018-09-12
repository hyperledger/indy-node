import pytest

from indy_common.constants import CRED_DEF_ID
from indy_common.types import Request
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.util import randomString


def test_validation_cred_def_not_present(build_revoc_def_by_default,
                                         create_node_and_not_start):
    node = create_node_and_not_start
    req = build_revoc_def_by_default
    req_handler = node.getDomainReqHandler()
    with pytest.raises(InvalidClientRequest, match="There is no any CRED_DEF"):
        req_handler.validate(Request(**req))


def test_invalid_cred_def_id_format(build_revoc_def_by_default,
                                    create_node_and_not_start):
    node = create_node_and_not_start
    req_handler = node.getDomainReqHandler()
    req = build_revoc_def_by_default

    req['operation'][CRED_DEF_ID] = ":".join(3 * [randomString(10)])
    with pytest.raises(InvalidClientRequest, match="Format of {} field is not acceptable".format(CRED_DEF_ID)):
        req_handler.validate(Request(**req))

    req['operation'][CRED_DEF_ID] = ":".join(6 * [randomString(10)])
    with pytest.raises(InvalidClientRequest, match="Format of {} field is not acceptable".format(CRED_DEF_ID)):
        req_handler.validate(Request(**req))
