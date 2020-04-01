from typing import NamedTuple

from plenum.common.constants import TXN_TYPE, TARGET_NYM, ORIGIN, DATA, RAW, \
    ENC, HASH, NAME, VERSION, ALIAS, VERKEY, FORCE
from indy_common.roles import Roles
from indy_common.transactions import IndyTransactions

Environment = NamedTuple("Environment", [
    ("poolLedger", str),
    ("domainLedger", str)
])

DOMAIN_LEDGER_ID = 1

# SCHEMA
SCHEMA_NAME = "name"
SCHEMA_VERSION = "version"
SCHEMA_ATTR_NAMES = "attr_names"
SCHEMA_FROM = "dest"

# CLAIM DEF
CLAIM_DEF_SIGNATURE_TYPE = "signature_type"
CLAIM_DEF_SCHEMA_REF = "ref"
CLAIM_DEF_TAG = "tag"
CLAIM_DEF_PUBLIC_KEYS = "data"
CLAIM_DEF_FROM = "origin"
CLAIM_DEF_PRIMARY = "primary"
CLAIM_DEF_REVOCATION = "revocation"
CLAIM_DEF_TAG_DEFAULT = "tag"
CLAIM_DEF_CL = "CL"

# AUTH_RULE
CONSTRAINT = "constraint"
OLD_VALUE = "old_value"
NEW_VALUE = "new_value"
AUTH_ACTION = "auth_action"
AUTH_TYPE = "auth_type"
FIELD = "field"
RULES = "rules"

ROLE = 'role'
NONCE = 'nonce'
ATTRIBUTES = "attributes"
ACTION = 'action'
SCHEDULE = 'schedule'
DATETIME = 'datetime'
TIMEOUT = 'timeout'
SHA256 = 'sha256'
START = 'start'
CANCEL = 'cancel'
COMPLETE = 'complete'
IN_PROGRESS = 'in_progress'
FAIL = 'fail'
JUSTIFICATION = 'justification'
REINSTALL = 'reinstall'
SIGNATURE_TYPE = 'signature_type'
TAG = 'tag'
PACKAGE = 'package'

REVOC_TYPE = "revocDefType"
ID = "id"
CRED_DEF_ID = "credDefId"
ISSUANCE_TYPE = "issuanceType"
MAX_CRED_NUM = "maxCredNum"
PUBLIC_KEYS = "publicKeys"
TAILS_HASH = "tailsHash"
TAILS_LOCATION = "tailsLocation"
SUBMITTER_DID = "submitterDid"
VALUE = "value"
REQ_METADATA = "reqMetadata"
REVOC_REG_DEF_ID = "revocRegDefId"
PREV_ACCUM = "prevAccum"
ACCUM = "accum"
ACCUM_FROM = "accum_from"
ACCUM_TO = "accum_to"
ISSUED = "issued"
REVOKED = "revoked"
ISSUANCE_BY_DEFAULT = "ISSUANCE_BY_DEFAULT"
ISSUANCE_ON_DEMAND = "ISSUANCE_ON_DEMAND"
TIMESTAMP = 'timestamp'
FROM = "from"
TO = "to"
STATE_PROOF_FROM = "stateProofFrom"
REVOC_REG_ID = "revocRegId"

NULL = 'null'
OWNER = '<owner>'

LAST_TXN = "lastTxn"
TXNS = "Txns"

ENC_TYPE = "encType"
SKEY = "secretKey"
REF = "ref"
PRIMARY = "primary"
REVOCATION = "revocation"

WRITES = "writes"

RESTART_MESSAGE = "restart"
UPGRADE_MESSAGE = "upgrade"
MESSAGE_TYPE = "message_type"

allOpKeys = (
    TXN_TYPE,
    TARGET_NYM,
    VERKEY,
    ORIGIN,
    ROLE,
    DATA,
    NONCE,
    REF,
    RAW,
    ENC,
    HASH,
    ALIAS,
    ACTION,
    SCHEDULE,
    TIMEOUT,
    SHA256,
    START,
    CANCEL,
    NAME,
    VERSION,
    JUSTIFICATION,
    SIGNATURE_TYPE,
    FORCE,
    WRITES,
    REINSTALL)

reqOpKeys = (TXN_TYPE,)

# Attribute Names
ENDPOINT = "endpoint"

# Roles

# FIXME can be automated by iteration through Roles
# but it would be less self-descriptive
ENDORSER = Roles.ENDORSER.value
ENDORSER_STRING = 'ENDORSER'

NETWORK_MONITOR = Roles.NETWORK_MONITOR.value
NETWORK_MONITOR_STRING = 'NETWORK_MONITOR'

# client transaction types
NODE = IndyTransactions.NODE.value
NYM = IndyTransactions.NYM.value
ATTRIB = IndyTransactions.ATTRIB.value
SCHEMA = IndyTransactions.SCHEMA.value
CLAIM_DEF = IndyTransactions.CLAIM_DEF.value
REVOC_REG_DEF = IndyTransactions.REVOC_REG_DEF.value
REVOC_REG_ENTRY = IndyTransactions.REVOC_REG_ENTRY.value
DISCLO = IndyTransactions.DISCLO.value
GET_ATTR = IndyTransactions.GET_ATTR.value
GET_NYM = IndyTransactions.GET_NYM.value
GET_TXNS = IndyTransactions.GET_TXNS.value
GET_SCHEMA = IndyTransactions.GET_SCHEMA.value
GET_CLAIM_DEF = IndyTransactions.GET_CLAIM_DEF.value
GET_REVOC_REG_DEF = IndyTransactions.GET_REVOC_REG_DEF.value
GET_REVOC_REG = IndyTransactions.GET_REVOC_REG.value
GET_REVOC_REG_DELTA = IndyTransactions.GET_REVOC_REG_DELTA.value
CHANGE_KEY = IndyTransactions.CHANGE_KEY.value

POOL_UPGRADE = IndyTransactions.POOL_UPGRADE.value
NODE_UPGRADE = IndyTransactions.NODE_UPGRADE.value
POOL_RESTART = IndyTransactions.POOL_RESTART.value
VALIDATOR_INFO = IndyTransactions.VALIDATOR_INFO.value

POOL_CONFIG = IndyTransactions.POOL_CONFIG.value
AUTH_RULE = IndyTransactions.AUTH_RULE.value
AUTH_RULES = IndyTransactions.AUTH_RULES.value
GET_AUTH_RULE = IndyTransactions.GET_AUTH_RULE.value

# client Rich Schema transaction types
JSON_LD_CONTEXT = IndyTransactions.JSON_LD_CONTEXT.value
RICH_SCHEMA = IndyTransactions.RICH_SCHEMA.value
RICH_SCHEMA_ENCODING = IndyTransactions.RICH_SCHEMA_ENCODING.value
RICH_SCHEMA_MAPPING = IndyTransactions.RICH_SCHEMA_MAPPING.value
RICH_SCHEMA_CRED_DEF = IndyTransactions.RICH_SCHEMA_CRED_DEF.value
RICH_SCHEMA_PRES_DEF = IndyTransactions.RICH_SCHEMA_PRES_DEF.value
GET_RICH_SCHEMA_OBJECT_BY_ID = IndyTransactions.GET_RICH_SCHEMA_OBJECT_BY_ID.value
GET_RICH_SCHEMA_OBJECT_BY_METADATA = IndyTransactions.GET_RICH_SCHEMA_OBJECT_BY_METADATA.value

CONFIG_LEDGER_ID = 2
JUSTIFICATION_MAX_SIZE = 1000

LOCAL_AUTH_POLICY = 1
CONFIG_LEDGER_AUTH_POLICY = 2

TAG_LIMIT_SIZE = 256

APP_NAME = "indy-node"

# RICH SCHEMA
RS_ID = 'id'
RS_TYPE = 'rsType'
RS_NAME = 'rsName'
RS_VERSION = 'rsVersion'
RS_CONTENT = 'content'
RS_FROM = 'from'
RS_ENDORSER = 'endorser'

JSON_LD_CONTEXT_FIELD = "@context"
JSON_LD_ID_FIELD = "@id"
JSON_LD_TYPE_FIELD = "@type"

# RICH SCHEMA type names
RS_CONTEXT_TYPE_VALUE = 'ctx'
RS_SCHEMA_TYPE_VALUE = 'sch'
RS_ENCODING_TYPE_VALUE = 'enc'
RS_MAPPING_TYPE_VALUE = 'map'
RS_CRED_DEF_TYPE_VALUE = 'cdf'
RS_PRES_DEF_TYPE_VALUE = 'pdf'

# Specific Rich Schema Object's content fields:
RS_CRED_DEF_SIG_TYPE = "signatureType"
RS_CRED_DEF_MAPPING = "mapping"
RS_CRED_DEF_SCHEMA = "schema"
RS_CRED_DEF_PUB_KEY = "publicKey"

RS_ENC_INPUT = "input"
RS_ENC_OUTPUT = "output"
RS_ENC_ALGORITHM = "algorithm"
RS_ENC_TEST_VECS = "testVectors"
RS_ENC_ID = "id"
RS_ENC_TYPE = "type"
RS_ENC_ALG_DESC = "description"
RS_ENC_ALG_DOC = "documentation"
RS_ENC_ALG_IMPL = "implementation"

RS_MAPPING_ATTRIBUTES = "attributes"
RS_MAPPING_ISSUER = "issuer"
RS_MAPPING_ISSUANCE_DATE = "issuanceDate"
RS_MAPPING_SCHEMA = "schema"
RS_MAPPING_ENC = "enc"
RS_MAPPING_RANK = "rank"
