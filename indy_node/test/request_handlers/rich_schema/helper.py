import json

from indy_common.constants import SET_RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE, SET_RICH_SCHEMA_MAPPING, \
    RS_MAPPING_TYPE_VALUE, RS_CRED_DEF_TYPE_VALUE, SET_RICH_SCHEMA_CRED_DEF, SET_RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE, \
    SET_JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE, RS_ID, RS_NAME, RS_TYPE, RS_VERSION, RS_CONTENT
from indy_common.types import Request
from indy_node.test.context.helper import W3C_BASE_CONTEXT
from plenum.common.constants import TXN_TYPE, OP_VER
from plenum.common.txn_util import reqToTxn, append_txn_metadata
from plenum.common.util import randomString


def rs_req(txn_type, rs_type, content):
    author = randomString()
    endorser = randomString()
    return Request(identifier=author,
                   reqId=1234,
                   signatures={author: "sig1", endorser: "sig2"},
                   endorser=endorser,
                   operation={
                       TXN_TYPE: txn_type,
                       OP_VER: '1.1',
                       RS_ID: randomString(),
                       RS_NAME: randomString(),
                       RS_TYPE: rs_type,
                       RS_VERSION: '1.0',
                       RS_CONTENT: json.dumps(content)
                   })


def context_request():
    return rs_req(SET_JSON_LD_CONTEXT, RS_CONTEXT_TYPE_VALUE,
                  content=W3C_BASE_CONTEXT)


def rich_schema_request():
    return rs_req(SET_RICH_SCHEMA, RS_SCHEMA_TYPE_VALUE,
                  content={
                      "@id": "test_unique_id",
                      "@context": "ctx:sov:2f9F8ZmxuvDqRiqqY29x6dx9oU4qwFTkPbDpWtwGbdUsrCD",
                      "@type": "rdfs:Class",
                      "rdfs:comment": "ISO18013 International Driver License",
                      "rdfs:label": "Driver License",
                      "rdfs:subClassOf": {
                          "@id": "sch:Thing"
                      },
                      "driver": "Driver",
                      "dateOfIssue": "Date",
                      "dateOfExpiry": "Date",
                      "issuingAuthority": "Text",
                      "licenseNumber": "Text",
                      "categoriesOfVehicles": {
                          "vehicleType": "Text",
                          "vehicleType-input": {
                              "@type": "sch:PropertyValueSpecification",
                              "valuePattern": "^(A|B|C|D|BE|CE|DE|AM|A1|A2|B1|C1|D1|C1E|D1E)$"
                          },
                          "dateOfIssue": "Date",
                          "dateOfExpiry": "Date",
                          "restrictions": "Text",
                          "restrictions-input": {
                              "@type": "sch:PropertyValueSpecification",
                              "valuePattern": "^([A-Z]|[1-9])$"
                          }
                      },
                      "administrativeNumber": "Text"
                  })


def rich_schema_encoding_request():
    return rs_req(SET_RICH_SCHEMA_ENCODING, RS_ENCODING_TYPE_VALUE,
                  content={"test1": "test2"})


def rich_schema_mapping_request():
    return rs_req(SET_RICH_SCHEMA_MAPPING, RS_MAPPING_TYPE_VALUE,
                  content={"test1": "test2"})


def rich_schema_cred_def_request():
    return rs_req(SET_RICH_SCHEMA_CRED_DEF, RS_CRED_DEF_TYPE_VALUE,
                  content={"test1": "test2"})


def make_rich_schema_object_exist(handler, request):
    seq_no = 1
    txn_time = 1560241033
    txn = reqToTxn(request)
    append_txn_metadata(txn, seq_no, txn_time)
    handler.update_state(txn, None, context_request)
