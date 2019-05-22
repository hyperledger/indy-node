from indy_common.constants import NYM, NODE, ATTRIB, SCHEMA, CLAIM_DEF, DISCLO, GET_ATTR, GET_NYM, GET_TXNS, \
    GET_SCHEMA, GET_CLAIM_DEF, POOL_UPGRADE, NODE_UPGRADE, POOL_CONFIG, REVOC_REG_DEF, REVOC_REG_ENTRY, \
    GET_REVOC_REG_DEF, GET_REVOC_REG, GET_REVOC_REG_DELTA, POOL_RESTART, VALIDATOR_INFO, CHANGE_KEY, AUTH_RULE, \
    GET_AUTH_RULE, AUTH_RULES
from indy_common.transactions import IndyTransactions


def testTransactionsAreEncoded():
    assert NODE == "0"
    assert NYM == "1"
    assert GET_TXNS == "3"
    assert ATTRIB == "100"
    assert SCHEMA == "101"
    assert CLAIM_DEF == "102"
    assert DISCLO == "103"
    assert GET_ATTR == "104"
    assert GET_NYM == "105"
    assert GET_SCHEMA == "107"
    assert GET_CLAIM_DEF == "108"
    assert POOL_UPGRADE == "109"
    assert NODE_UPGRADE == "110"
    assert POOL_CONFIG == "111"
    assert CHANGE_KEY == "112"

    assert REVOC_REG_DEF == "113"
    assert REVOC_REG_ENTRY == "114"
    assert GET_REVOC_REG_DEF == "115"
    assert GET_REVOC_REG == "116"
    assert GET_REVOC_REG_DELTA == "117"

    assert POOL_RESTART == "118"
    assert VALIDATOR_INFO == "119"

    assert AUTH_RULE == "120"
    assert GET_AUTH_RULE == "121"
    assert AUTH_RULES == "122"


def testTransactionEnumDecoded():
    assert IndyTransactions.NODE.name == "NODE"
    assert IndyTransactions.NYM.name == "NYM"

    assert IndyTransactions.ATTRIB.name == "ATTRIB"
    assert IndyTransactions.SCHEMA.name == "SCHEMA"
    assert IndyTransactions.CLAIM_DEF.name == "CLAIM_DEF"

    assert IndyTransactions.DISCLO.name == "DISCLO"

    assert IndyTransactions.GET_ATTR.name == "GET_ATTR"
    assert IndyTransactions.GET_NYM.name == "GET_NYM"
    assert IndyTransactions.GET_TXNS.name == "GET_TXNS"
    assert IndyTransactions.GET_SCHEMA.name == "GET_SCHEMA"
    assert IndyTransactions.GET_CLAIM_DEF.name == "GET_CLAIM_DEF"

    assert IndyTransactions.POOL_UPGRADE.name == "POOL_UPGRADE"
    assert IndyTransactions.NODE_UPGRADE.name == "NODE_UPGRADE"
    assert IndyTransactions.POOL_CONFIG.name == "POOL_CONFIG"
    assert IndyTransactions.POOL_RESTART.name == "POOL_RESTART"
    assert IndyTransactions.CHANGE_KEY.name == "CHANGE_KEY"

    assert IndyTransactions.REVOC_REG_DEF.name == "REVOC_REG_DEF"
    assert IndyTransactions.REVOC_REG_ENTRY.name == "REVOC_REG_ENTRY"
    assert IndyTransactions.GET_REVOC_REG_DEF.name == "GET_REVOC_REG_DEF"
    assert IndyTransactions.GET_REVOC_REG.name == "GET_REVOC_REG"
    assert IndyTransactions.GET_REVOC_REG_DELTA.name == "GET_REVOC_REG_DELTA"

    assert IndyTransactions.VALIDATOR_INFO.name == "VALIDATOR_INFO"


def testTransactionEnumEncoded():
    assert IndyTransactions.NODE.value == "0"
    assert IndyTransactions.NYM.value == "1"
    assert IndyTransactions.GET_TXNS.value == "3"

    assert IndyTransactions.ATTRIB.value == "100"
    assert IndyTransactions.SCHEMA.value == "101"
    assert IndyTransactions.CLAIM_DEF.value == "102"

    assert IndyTransactions.DISCLO.value == "103"
    assert IndyTransactions.GET_ATTR.value == "104"
    assert IndyTransactions.GET_NYM.value == "105"
    assert IndyTransactions.GET_SCHEMA.value == "107"
    assert IndyTransactions.GET_CLAIM_DEF.value == "108"
    assert IndyTransactions.POOL_UPGRADE.value == "109"
    assert IndyTransactions.NODE_UPGRADE.value == "110"
    assert IndyTransactions.POOL_CONFIG.value == "111"
    assert IndyTransactions.CHANGE_KEY.value == "112"
    assert IndyTransactions.REVOC_REG_DEF.value == "113"
    assert IndyTransactions.REVOC_REG_ENTRY.value == "114"
    assert IndyTransactions.GET_REVOC_REG_DEF.value == "115"
    assert IndyTransactions.GET_REVOC_REG.value == "116"
    assert IndyTransactions.GET_REVOC_REG_DELTA.value == "117"
    assert IndyTransactions.POOL_RESTART.value == "118"
    assert IndyTransactions.VALIDATOR_INFO.value == "119"


def test_get_name_from_code():
    assert IndyTransactions.get_name_from_code(IndyTransactions.NODE.value) == "NODE"
    assert IndyTransactions.get_name_from_code(IndyTransactions.NYM.value) == "NYM"

    assert IndyTransactions.get_name_from_code(IndyTransactions.ATTRIB.value) == "ATTRIB"
    assert IndyTransactions.get_name_from_code(IndyTransactions.SCHEMA.value) == "SCHEMA"
    assert IndyTransactions.get_name_from_code(IndyTransactions.CLAIM_DEF.value) == "CLAIM_DEF"

    assert IndyTransactions.get_name_from_code(IndyTransactions.DISCLO.value) == "DISCLO"
    assert IndyTransactions.get_name_from_code(IndyTransactions.GET_ATTR.value) == "GET_ATTR"
    assert IndyTransactions.get_name_from_code(IndyTransactions.GET_NYM.value) == "GET_NYM"
    assert IndyTransactions.get_name_from_code(IndyTransactions.GET_TXNS.value) == "GET_TXNS"
    assert IndyTransactions.get_name_from_code(IndyTransactions.GET_SCHEMA.value) == "GET_SCHEMA"
    assert IndyTransactions.get_name_from_code(IndyTransactions.GET_CLAIM_DEF.value) == "GET_CLAIM_DEF"
    assert IndyTransactions.get_name_from_code(IndyTransactions.POOL_UPGRADE.value) == "POOL_UPGRADE"
    assert IndyTransactions.get_name_from_code(IndyTransactions.NODE_UPGRADE.value) == "NODE_UPGRADE"
    assert IndyTransactions.get_name_from_code(IndyTransactions.POOL_CONFIG.value) == "POOL_CONFIG"
    assert IndyTransactions.get_name_from_code(IndyTransactions.POOL_RESTART.value) == "POOL_RESTART"

    assert IndyTransactions.get_name_from_code(IndyTransactions.CHANGE_KEY.value) == "CHANGE_KEY"
    assert IndyTransactions.get_name_from_code(IndyTransactions.REVOC_REG_DEF.value) == "REVOC_REG_DEF"
    assert IndyTransactions.get_name_from_code(IndyTransactions.REVOC_REG_ENTRY.value) == "REVOC_REG_ENTRY"
    assert IndyTransactions.get_name_from_code(IndyTransactions.GET_REVOC_REG_DEF.value) == "GET_REVOC_REG_DEF"
    assert IndyTransactions.get_name_from_code(IndyTransactions.GET_REVOC_REG.value) == "GET_REVOC_REG"
    assert IndyTransactions.get_name_from_code(IndyTransactions.GET_REVOC_REG_DELTA.value) == "GET_REVOC_REG_DELTA"
    assert IndyTransactions.get_name_from_code(IndyTransactions.VALIDATOR_INFO.value) == "VALIDATOR_INFO"

    assert IndyTransactions.get_name_from_code("some_unexpected_code") == "Unknown_transaction_type"
