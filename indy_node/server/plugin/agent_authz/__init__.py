from indy_node.server.plugin.agent_authz.constants import AGENT_AUTHZ, \
    GET_AGENT_AUTHZ_ACCUM
from indy_node.server.plugin.agent_authz.messages.types import \
    ClientAgentAuthzAccumGetOperation, ClientAgentAuthzSubmitOperation
from indy_node.server.plugin.agent_authz.transactions import \
    AgentAuthzTransactions

AcceptableWriteTypes = {AgentAuthzTransactions.AGENT_AUTHZ.value}

AcceptableQueryTypes = {AgentAuthzTransactions.GET_AGENT_AUTHZ.value,
                        AgentAuthzTransactions.GET_AGENT_AUTHZ_ACCUM.value}

REQ_OP_TYPES = {AGENT_AUTHZ: ClientAgentAuthzSubmitOperation,
                GET_AGENT_AUTHZ_ACCUM: ClientAgentAuthzAccumGetOperation}
