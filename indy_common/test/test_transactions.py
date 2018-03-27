from indy_common.constants import NYM, NODE, ATTRIB, SCHEMA, CLAIM_DEF, DISCLO, GET_ATTR, GET_NYM, GET_TXNS, \
    GET_SCHEMA, GET_CLAIM_DEF, POOL_UPGRADE, NODE_UPGRADE, POOL_CONFIG
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
    assert IndyTransactions.POOL_RESTART.value == "118"
