import json

from indy.ledger import build_nym_request, sign_request, submit_request, build_attrib_request
from indy_client.test.cli.helper import createHalfKeyIdentifierAndAbbrevVerkey, logger


def validate_txn(txn):
    assert 'type' in txn
    assert 'data' in txn
    assert 'metadata' in txn


def validate_txn_metadata(txn_metadata):
    assert 'txnTime' in txn_metadata
    assert 'seqNo' in txn_metadata
    assert 'txnId' in txn_metadata


def validate_req_signature(req_signature):
    assert 'type' in req_signature
    assert 'values' in req_signature
    for value in req_signature['values']:
        assert 'from' in value
        assert 'value' in value


def validate_write_result(result):
    assert 'ver' in result
    assert 'txn' in result
    assert 'txnMetadata' in result
    assert 'reqSignature' in result
    assert 'rootHash' in result
    assert 'auditPath' in result

    validate_txn(result['txn'])
    validate_txn_metadata(result['txnMetadata'])
    validate_req_signature(result['req_signature'])


def test_nym_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    idr, verkey = createHalfKeyIdentifierAndAbbrevVerkey()

    wallet_handle, identifier = sdk_wallet_steward

    request = looper.loop.run_until_complete(build_nym_request(identifier, idr, verkey, None, None))
    req_signed = looper.loop.run_until_complete(sign_request(wallet_handle, identifier, request))
    reply = json.loads(looper.loop.run_until_complete(submit_request(sdk_pool_handle, req_signed)))

    validate_write_result(reply['result'])
