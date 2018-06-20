import json
import base58

from indy.ledger import build_nym_request, sign_request, submit_request, build_attrib_request
from indy_client.test.cli.helper import createHalfKeyIdentifierAndAbbrevVerkey, logger


# Utility predicates

def is_one_of(*args):
    def check(v):
        return v in args

    return check


def is_int(v):
    return isinstance(v, int)


def is_list(v):
    return isinstance(v, list)


def is_dict(v):
    return isinstance(v, dict)


def is_str(v):
    return isinstance(v, str)


def is_base58_str(v):
    return is_str(v) and all(c in base58.alphabet for c in v.encode())


def is_number_str(v):
    return is_str(v) and v.isdigit()


# Basic requirement checkers

def require(d, k, t):
    assert k in d
    assert t(d[k])


def optional(d, k, t):
    if k in d:
        assert t(d[k])


# Validators

def validate_txn(txn):
    require(txn, 'type', is_number_str)
    require(txn, 'data', is_dict)
    require(txn, 'metadata', is_dict)
    optional(txn, 'protocolVersion', is_int)

    metadata = txn['metadata']
    require(metadata, 'from', is_base58_str)
    require(metadata, 'reqId', is_int)


def validate_txn_metadata(txn_metadata):
    require(txn_metadata, 'txnTime', is_int)
    require(txn_metadata, 'seqNo', is_int)
    require(txn_metadata, 'txnId', is_str)


def validate_req_signature(req_signature):
    require(req_signature, 'type', is_one_of('ED25519', 'ED25519_MULTI'))
    require(req_signature, 'values', is_list)
    for value in req_signature['values']:
        require(value, 'from', is_base58_str)
        require(value, 'value', is_base58_str)


def validate_write_result(result):
    require(result, 'ver', is_str)
    require(result, 'txn', is_dict)
    require(result, 'txnMetadata', is_dict)
    require(result, 'reqSignature', is_dict)
    require(result, 'rootHash', is_base58_str)
    require(result, 'auditPath', is_list)
    assert all(is_base58_str(v) for v in result['auditPath'])

    validate_txn(result['txn'])
    validate_txn_metadata(result['txnMetadata'])
    validate_req_signature(result['reqSignature'])


# Tests

def test_nym_reply_is_valid(looper, sdk_pool_handle, sdk_wallet_steward):
    idr, verkey = createHalfKeyIdentifierAndAbbrevVerkey()

    wallet_handle, identifier = sdk_wallet_steward

    request = looper.loop.run_until_complete(build_nym_request(identifier, idr, verkey, None, None))
    req_signed = looper.loop.run_until_complete(sign_request(wallet_handle, identifier, request))
    reply = json.loads(looper.loop.run_until_complete(submit_request(sdk_pool_handle, req_signed)))

    validate_write_result(reply['result'])
