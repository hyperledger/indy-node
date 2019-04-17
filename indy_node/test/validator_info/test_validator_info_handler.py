import pytest

from indy_common.constants import VALIDATOR_INFO
from plenum.common.constants import TXN_TYPE, DATA
from plenum.common.types import f
from plenum.test.helper import sdk_gen_request, sdk_sign_request_objects


def test_validator_info_handler(monkeypatch,
                                sdk_wallet_trustee,
                                txnPoolNodeSet,
                                looper):

    op = {
        TXN_TYPE: VALIDATOR_INFO
    }
    req_obj = sdk_gen_request(op, identifier=sdk_wallet_trustee[1])
    req_obj.signature = "signature"

    def is_ack(req_key, frm):
        assert (req_obj.identifier, req_obj.reqId) == req_key

    def is_reply_correct(resp, frm):
        _comparison_reply(resp, req_obj)

    node = txnPoolNodeSet[0]
    monkeypatch.setattr(node, 'transmitToClient', is_reply_correct)
    monkeypatch.setattr(node, 'send_ack_to_client', is_ack)
    node.process_action(req_obj, None)


def _comparison_reply(resp, req_obj):
    assert resp.result[f.IDENTIFIER.nm] == req_obj.identifier
    assert resp.result[f.REQ_ID.nm] == req_obj.reqId
    assert resp.result[TXN_TYPE] == VALIDATOR_INFO
    assert resp.result[DATA] is not None


