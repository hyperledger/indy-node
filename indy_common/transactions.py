from plenum.common.transactions import Transactions, PlenumTransactions


class IndyTransactions(Transactions):
    #  These numeric constants CANNOT be changed once they have been used,
    #  because that would break backwards compatibility with the ledger
    #  Also the numeric constants CANNOT collide with transactions in plenum
    NODE = PlenumTransactions.NODE.value
    NYM = PlenumTransactions.NYM.value
    ATTRIB = "100"
    SCHEMA = "101"
    CLAIM_DEF = "102"

    DISCLO = "103"
    GET_ATTR = "104"
    GET_NYM = "105"
    GET_TXNS = PlenumTransactions.GET_TXN.value
    GET_SCHEMA = "107"
    GET_CLAIM_DEF = "108"

    POOL_UPGRADE = "109"
    NODE_UPGRADE = "110"

    POOL_CONFIG = "111"

    CHANGE_KEY = "112"

    REVOC_REG_DEF = "113"
    REVOC_REG_ENTRY = "114"
    GET_REVOC_REG_DEF = "115"
    GET_REVOC_REG = "116"
    GET_REVOC_REG_DELTA = "117"

    POOL_RESTART = "118"
    VALIDATOR_INFO = "119"

    AUTH_RULE = "120"
    GET_AUTH_RULE = "121"
    AUTH_RULES = "122"

    # Rich Schema
    JSON_LD_CONTEXT = "200"
    RICH_SCHEMA = "201"
    RICH_SCHEMA_ENCODING = "202"
    RICH_SCHEMA_MAPPING = "203"
    RICH_SCHEMA_CRED_DEF = "204"
    RICH_SCHEMA_PRES_DEF = "205"
    GET_RICH_SCHEMA_OBJECT_BY_ID = "300"
    GET_RICH_SCHEMA_OBJECT_BY_METADATA = "301"

    @staticmethod
    def get_name_from_code(code: str):
        try:
            return IndyTransactions(code).name
        except ValueError:
            return "Unknown_transaction_type"
