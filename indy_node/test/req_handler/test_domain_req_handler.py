import pytest
from plenum.common.constants import TXN_TYPE, NYM, TARGET_NYM, VERKEY, DATA, STATE_PROOF, TXN_TIME
from plenum.common.plenum_protocol_version import PlenumProtocolVersion
from plenum.common.types import f
from plenum.common.util import get_utc_epoch

from indy_common.types import SafeRequest
from indy_node.server.domain_req_handler import DomainReqHandler


@pytest.fixture()
def operation():
    return {
        TXN_TYPE: NYM,
        TARGET_NYM: 'HebGWgHmicPtzr4BTHmSmXkDNL7CngDjYVcxqT5oprMw',
        VERKEY: '~A43KHjJmjwFX71J1b5p61N'
    }


def check_make_result(request, should_have_proof):
    data = {NYM: 'HebGWgHmicPtzr4BTHmSmXkDNL7CngDjYVcxqT5oprMw'}
    seq_no = 5
    txn_time = get_utc_epoch()
    proof = [b"proof1"]
    result = DomainReqHandler.make_result(request=request,
                                          data=data,
                                          last_seq_no=seq_no,
                                          update_time=txn_time,
                                          proof=proof)
    assert result

    # operation part:
    assert result[TXN_TYPE] == NYM
    assert result[TARGET_NYM] == 'HebGWgHmicPtzr4BTHmSmXkDNL7CngDjYVcxqT5oprMw'
    assert result[VERKEY] == '~A43KHjJmjwFX71J1b5p61N'

    assert result[DATA] == data
    assert result[f.IDENTIFIER.nm] == request.identifier
    assert result[f.REQ_ID.nm] == request.reqId
    assert result[f.SEQ_NO.nm] == seq_no
    assert result[TXN_TIME] == txn_time

    # check proof
    if should_have_proof:
        assert result[STATE_PROOF] == proof
    else:
        assert STATE_PROOF not in result


def test_make_result_no_protocol_version_by_default(operation):
    request = SafeRequest(identifier="1" * 16,
                          reqId=1,
                          operation=operation,
                          signature="signature")
    check_make_result(request, should_have_proof=False)


def test_make_result_protocol_version_state_proof(operation):
    request = SafeRequest(identifier="1" * 16,
                          reqId=1,
                          operation=operation,
                          signature="signature")
    request.protocolVersion = PlenumProtocolVersion.STATE_PROOF_SUPPORT.value
    check_make_result(request, should_have_proof=True)


def test_make_result_no_protocol_version(operation):
    request = SafeRequest(identifier="1" * 16,
                          reqId=1,
                          operation=operation,
                          signature="signature")
    request.protocolVersion = None
    check_make_result(request, should_have_proof=False)


def test_make_result_protocol_version_less_than_state_proof(operation):
    request = SafeRequest(identifier="1" * 16,
                          reqId=1,
                          operation=operation,
                          signature="signature")
    request.protocolVersion = 0
    check_make_result(request, should_have_proof=False)
