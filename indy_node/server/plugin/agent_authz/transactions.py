from plenum.common.transactions import Transactions

# DO NOT CHANGE ONCE CODE IS DEPLOYED ON THE LEDGER
PREFIX = '3000'


class AgentAuthzTransactions(Transactions):
    AGENT_AUTHZ = PREFIX + '0'
    GET_AGENT_AUTHZ = PREFIX + '1'
    GET_AGENT_AUTHZ_ACCUM = PREFIX + '2'
    GET_AGENT_AUTHZ_ACCUM_WIT = PREFIX + '3'
