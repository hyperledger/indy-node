from indy_node.server.plugin.agent_authz.constants import AGENT_AUTHZ, ADDRESS, \
    AUTHORIZATION, COMMITMENT, GET_AGENT_AUTHZ_ACCUM, ACCUMULATOR_ID, \
    ACCUMULATOR_1, ACCUMULATOR_2
from indy_node.server.plugin.agent_authz.messages.fields import \
    AgentAuthzPolicyAddressField, AgentAuthzCommitmentField, \
    AgentAuthzAuthorisationField, AgentAuthzAccumIdField
from plenum.common.constants import TXN_TYPE, VERKEY
from plenum.common.messages.fields import ConstantField, FullVerkeyField
from plenum.common.messages.message_base import MessageValidator


class ClientAgentAuthzSubmitOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(AGENT_AUTHZ)),
        # Temporary value, needs to change
        (ADDRESS, AgentAuthzPolicyAddressField(1000000)),
        (VERKEY, FullVerkeyField(optional=True)),
        # Temporary value, needs to change
        (AUTHORIZATION, AgentAuthzAuthorisationField(128, optional=True)),
        # Temporary value, needs to change
        (COMMITMENT, AgentAuthzCommitmentField(199, optional=True)),
    )


class ClientAgentAuthzAccumGetOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(GET_AGENT_AUTHZ_ACCUM)),
        (ACCUMULATOR_ID, AgentAuthzAccumIdField(ACCUMULATOR_1, ACCUMULATOR_2)),
    )


class ClientAgentAuthzPolicyGetOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(GET_AGENT_AUTHZ_ACCUM)),
        (ADDRESS, AgentAuthzPolicyAddressField(1000000)),
    )
