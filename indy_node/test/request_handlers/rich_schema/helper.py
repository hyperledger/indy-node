import copy
import json

from indy_common.constants import RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, RICH_SCHEMA_MAPPING, \
    RS_MAPPING_TYPE_VALUE, RS_CRED_DEF_TYPE_VALUE, RICH_SCHEMA_CRED_DEF, RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, \
    JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, RS_ID, RS_NAME, RS_TYPE, RS_VERSION, RS_CONTENT, RS_PRES_DEF_TYPE_VALUE, \
    RICH_SCHEMA_PRES_DEF
from indy_common.types import Request
from indy_node.test.rich_schema.templates import RICH_SCHEMA_EX1, W3C_BASE_CONTEXT, RICH_SCHEMA_ENCODING_EX1, \
    RICH_SCHEMA_MAPPING_EX1, RICH_SCHEMA_CRED_DEF_EX1, RICH_SCHEMA_PRES_DEF_EX1
from plenum.common.constants import TXN_TYPE, OP_VER, CURRENT_PROTOCOL_VERSION
from plenum.common.txn_util import reqToTxn, append_txn_metadata
from plenum.common.util import randomString


def rs_req(txn_type, rs_type, content, id=None):
    author = randomString()
    endorser = randomString()
    return Request(identifier=author,
                   reqId=1234,
                   signatures={author: "sig1", endorser: "sig2"},
                   endorser=endorser,
                   protocolVersion=CURRENT_PROTOCOL_VERSION,
                   operation={
                       TXN_TYPE: txn_type,
                       OP_VER: '1.1',
                       RS_ID: id or randomString(),
                       RS_NAME: randomString(),
                       RS_TYPE: rs_type,
                       RS_VERSION: '1.0',
                       RS_CONTENT: json.dumps(content)
                   })


def context_request():
    return rs_req(JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE,
                  content=W3C_BASE_CONTEXT)


def rich_schema_request():
    id = randomString()
    content = copy.deepcopy(RICH_SCHEMA_EX1)
    content['@id'] = id
    return rs_req(RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE,
                  content=content, id=id)


def rich_schema_encoding_request():
    return rs_req(RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE,
                  content=RICH_SCHEMA_ENCODING_EX1)


def rich_schema_mapping_request():
    id = randomString()
    content = copy.deepcopy(RICH_SCHEMA_MAPPING_EX1)
    content['@id'] = id
    return rs_req(RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE,
                  content=content, id=id)


def rich_schema_cred_def_request():
    return rs_req(RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE,
                  content=RICH_SCHEMA_CRED_DEF_EX1)


def rich_schema_pres_def_request():
    id = randomString()
    content = copy.deepcopy(RICH_SCHEMA_PRES_DEF_EX1)
    content['@id'] = id
    return rs_req(RICH_SCHEMA_PRES_DEF, RS_PRES_DEF_TYPE_VALUE,
                  content=content, id=id)


def make_rich_schema_object_exist(handler, request, commit=False):
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(request)
    append_txn_metadata(txn, seq_no, txn_time)
    handler.update_state(txn, None, context_request)
    if commit:
        handler.state.commit()
