import pytest

from indy_common.constants import ENDORSER, NETWORK_MONITOR
from indy_common.test.constants import IDENTIFIERS, OTHER_ROLE
from indy_common.types import Request
from indy_node.server.request_handlers.config_req_handlers.txn_author_agreement_disable_handler import \
    TxnAuthorAgreementDisableHandler
from indy_node.test.conftest import write_auth_req_validator, idr_cache
from plenum.common.constants import TXN_TYPE, TXN_AUTHOR_AGREEMENT_DISABLE, TRUSTEE, STEWARD
from plenum.common.exceptions import UnauthorizedClientRequest


@pytest.fixture()
def disable_taa_handler(db_manager, write_auth_req_validator):
    return TxnAuthorAgreementDisableHandler(database_manager=db_manager,
                                            write_req_validator=write_auth_req_validator)


@pytest.fixture(params=[TRUSTEE, ENDORSER, STEWARD, NETWORK_MONITOR, None, OTHER_ROLE])
def disable_taa_request(request):
    operation = {TXN_TYPE: TXN_AUTHOR_AGREEMENT_DISABLE}
    return (request.param, Request(identifier=IDENTIFIERS[request.param][0],
                                   signature="sign",
                                   operation=operation))

def test_taa_disable_only_for_trustee(disable_taa_handler,
                                      disable_taa_request):
    who, req = disable_taa_request
    if who != TRUSTEE:
        with pytest.raises(UnauthorizedClientRequest, match="Not enough TRUSTEE signatures"):
            disable_taa_handler.authorize(req)
    else:
        disable_taa_handler.authorize(req)