from indy_node.server.plugin.agent_authz.constants import AGENT_AUTHZ, ADDRESS, \
    AUTHORIZATION, COMMITMENT, GET_AGENT_AUTHZ_ACCUM, ACCUMULATOR_ID, \
    ACCUMULATOR_1, ACCUMULATOR_2
from indy_node.server.plugin.agent_authz.messages.fields import \
    AgentAuthzPolicyAddressField, AgentAuthzCommitmentField, \
    AgentAuthzAuthorisationField, AgentAuthzAccumIdField
from plenum.common.constants import TXN_TYPE, VERKEY
from plenum.common.messages.fields import ConstantField, FullVerkeyField
from plenum.common.messages.message_base import MessageValidator


# Temporary value, needs to change
MAX_POLICY_ADDRESS = 1000000
# Temporary value, needs to change
MAX_COMMITMENT = 104729


class ClientAgentAuthzSubmitOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(AGENT_AUTHZ)),
        (ADDRESS, AgentAuthzPolicyAddressField(MAX_POLICY_ADDRESS)),
        (VERKEY, FullVerkeyField(optional=True)),
        # Temporary value, needs to change
        (AUTHORIZATION, AgentAuthzAuthorisationField(128, optional=True)),
        (COMMITMENT, AgentAuthzCommitmentField(MAX_COMMITMENT, optional=True)),
    )


class ClientAgentAuthzAccumGetOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(GET_AGENT_AUTHZ_ACCUM)),
        (ACCUMULATOR_ID, AgentAuthzAccumIdField(ACCUMULATOR_1, ACCUMULATOR_2)),
    )


class ClientAgentAuthzPolicyGetOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(GET_AGENT_AUTHZ_ACCUM)),
        (ADDRESS, AgentAuthzPolicyAddressField(MAX_POLICY_ADDRESS)),
    )
