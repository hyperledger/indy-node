import pytest
from indy_common.types import Request
from plenum.common.exceptions import InvalidClientRequest


def test_validation_cred_def_not_present(build_revoc_def_by_default,
                                         create_node_and_not_start):
    node = create_node_and_not_start
    req = build_revoc_def_by_default
    req_handler = node.getDomainReqHandler()
    with pytest.raises(InvalidClientRequest, match="There is no any CRED_DEF"):
        req_handler.validate(Request(**req))

