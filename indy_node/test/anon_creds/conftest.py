import pytest
import time
from contextlib import ExitStack
from plenum.common.util import randomString
from indy_common.constants import REVOC_REG_ENTRY, REVOC_REG_DEF_ID, ISSUED, \
    REVOKED, PREV_ACCUM, ACCUM, TYPE, REVOC_REG_DEF, ISSUANCE_BY_DEFAULT, \
    CRED_DEF_ID, VALUE, TAG, ISSUANCE_ON_DEMAND
from indy_common.types import Request
from indy_common.state import domain
from plenum.test.helper import sdk_sign_request_from_dict
from plenum.common.txn_util import reqToTxn
from plenum.common.types import f
from plenum.common.constants import TXN_TIME
from plenum.test.helper import create_new_test_node


@pytest.fixture(scope="module")
def create_node_and_not_start(testNodeClass,
                              node_config_helper_class,
                              tconf,
                              tdir,
                              allPluginsPath,
                              looper,
                              tdirWithPoolTxns,
                              tdirWithDomainTxns,
                              tdirWithNodeKeepInited):
    with ExitStack() as exitStack:
        node = exitStack.enter_context(create_new_test_node(testNodeClass,
                                node_config_helper_class,
                                "Alpha",
                                tconf,
                                tdir,
                                allPluginsPath))
        yield node

@pytest.fixture(scope="module")
def build_revoc_def_by_default(looper, sdk_wallet_steward):
    data = {
        "id": randomString(50),
        "type": REVOC_REG_DEF,
        "tag": randomString(5),
        "credDefId": randomString(50),
        "value":{
            "issuanceType": ISSUANCE_BY_DEFAULT,
            "maxCredNum": 1000000,
            "tailsHash": randomString(50),
            "tailsLocation": 'http://tails.location.com',
            "publicKeys": {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return req

@pytest.fixture(scope="module")
def add_revoc_def_by_default(create_node_and_not_start,
                  looper,
                  sdk_wallet_steward):
    node = create_node_and_not_start
    data = {
        "id": randomString(50),
        "type": REVOC_REG_DEF,
        "tag": randomString(5),
        "credDefId": randomString(50),
        "value":{
            "issuanceType": ISSUANCE_BY_DEFAULT,
            "maxCredNum": 1000000,
            "tailsHash": randomString(50),
            "tailsLocation": 'http://tails.location.com',
            "publicKeys": {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)

    req_handler = node.getDomainReqHandler()
    req_handler.validate(Request(**req))
    txn = reqToTxn(Request(**req))
    txn[f.SEQ_NO.nm] = node.domainLedger.seqNo + 1
    txn[TXN_TIME] = int(time.time())
    req_handler._addRevocDef(txn)
    return req

@pytest.fixture(scope="module")
def build_txn_for_revoc_def_entry_by_default(looper,
                                  sdk_wallet_steward,
                                  add_revoc_def_by_default):
    revoc_def_txn = add_revoc_def_by_default
    revoc_def_txn = reqToTxn(revoc_def_txn)
    path = ":".join([revoc_def_txn[f.IDENTIFIER.nm],
                     domain.MARKER_REVOC_DEF,
                     revoc_def_txn[CRED_DEF_ID],
                     revoc_def_txn[TYPE],
                     revoc_def_txn[TAG]])
    data = {
        REVOC_REG_DEF_ID: path,
        TYPE: REVOC_REG_ENTRY,
        VALUE: {
            PREV_ACCUM: randomString(10),
            ACCUM: randomString(10),
            ISSUED: [],
            REVOKED: [],
        }
    }

    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return req

@pytest.fixture(scope="module")
def add_revoc_def_by_demand(create_node_and_not_start,
                  looper,
                  sdk_wallet_steward):
    node = create_node_and_not_start
    data = {
        "id": randomString(50),
        "type": REVOC_REG_DEF,
        "tag": randomString(5),
        "credDefId": randomString(50),
        "value":{
            "issuanceType": ISSUANCE_ON_DEMAND,
            "maxCredNum": 1000000,
            "tailsHash": randomString(50),
            "tailsLocation": 'http://tails.location.com',
            "publicKeys": {},
        }
    }
    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)

    req_handler = node.getDomainReqHandler()
    req_handler.validate(Request(**req))
    txn = reqToTxn(Request(**req))
    txn[f.SEQ_NO.nm] = node.domainLedger.seqNo + 1
    txn[TXN_TIME] = int(time.time())
    req_handler._addRevocDef(txn)
    return req

@pytest.fixture(scope="module")
def build_txn_for_revoc_def_entry_by_demand(looper,
                                  sdk_wallet_steward,
                                  add_revoc_def_by_demand):
    revoc_def_txn = add_revoc_def_by_demand
    revoc_def_txn = reqToTxn(revoc_def_txn)
    path = ":".join([revoc_def_txn[f.IDENTIFIER.nm],
                     domain.MARKER_REVOC_DEF,
                     revoc_def_txn[CRED_DEF_ID],
                     revoc_def_txn[TYPE],
                     revoc_def_txn[TAG]])
    data = {
        REVOC_REG_DEF_ID: path,
        TYPE: REVOC_REG_ENTRY,
        VALUE: {
            PREV_ACCUM: randomString(10),
            ACCUM: randomString(10),
            ISSUED: [],
            REVOKED: [],
        }
    }

    req = sdk_sign_request_from_dict(looper, sdk_wallet_steward, data)
    return req
