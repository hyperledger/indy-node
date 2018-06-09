from indy_common.constants import SCHEMA_NAME, SCHEMA_VERSION, SCHEMA_ATTR_NAMES, SCHEMA_FROM, \
    CLAIM_DEF_SIGNATURE_TYPE, CLAIM_DEF_SCHEMA_REF, CLAIM_DEF_TAG, CLAIM_DEF_PUBLIC_KEYS, CLAIM_DEF_FROM, \
    CLAIM_DEF_TAG_DEFAULT, CLAIM_DEF_CL
from indy_common.types import Request

# SCHEMA
from plenum.common.constants import DATA
from plenum.common.types import OPERATION


def get_write_schema_name(req):
    if isinstance(req, Request):
        req = req.as_dict
    return req[OPERATION][DATA][SCHEMA_NAME]


def get_write_schema_version(req: Request):
    if isinstance(req, Request):
        req = req.as_dict
    return req[OPERATION][DATA][SCHEMA_VERSION]


def get_write_schema_attr_names(req: Request):
    if isinstance(req, Request):
        req = req.as_dict
    return req[OPERATION][DATA][SCHEMA_ATTR_NAMES]


def get_read_schema_name(req: Request):
    return req.operation[DATA][SCHEMA_NAME]


def get_read_schema_version(req: Request):
    return req.operation[DATA][SCHEMA_VERSION]


def get_read_schema_from(req: Request):
    return req.operation[SCHEMA_FROM]


# CLAIM DEF

def get_write_claim_def_signature_type(req: Request):
    if isinstance(req, Request):
        req = req.as_dict
    return req[OPERATION][CLAIM_DEF_SIGNATURE_TYPE]


def get_write_claim_def_schema_ref(req: Request):
    if isinstance(req, Request):
        req = req.as_dict
    return req[OPERATION][CLAIM_DEF_SCHEMA_REF]


def get_write_claim_def_tag(req: Request):
    if isinstance(req, Request):
        req = req.as_dict
    return req[OPERATION][CLAIM_DEF_TAG]


def get_write_claim_def_public_keys(req: Request):
    if isinstance(req, Request):
        req = req.as_dict
    return req[OPERATION][CLAIM_DEF_PUBLIC_KEYS]


def get_read_claim_def_signature_type(req: Request):
    return req.operation.get(CLAIM_DEF_SIGNATURE_TYPE, CLAIM_DEF_CL)


def get_read_claim_def_schema_ref(req: Request):
    return req.operation[CLAIM_DEF_SCHEMA_REF]


def get_read_claim_def_tag(req: Request):
    return req.operation.get(CLAIM_DEF_TAG, CLAIM_DEF_TAG_DEFAULT)


def get_read_claim_def_from(req: Request):
    return req.operation[CLAIM_DEF_FROM]
