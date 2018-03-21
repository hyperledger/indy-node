from indy_node.server.plugin.agent_authz.constants import AGENT_AUTHZ, ADDRESS, \
    AUTHORIZATION, COMMITMENT, GET_AGENT_AUTHZ_ACCUM, ACCUMULATOR_ID, \
    ACCUMULATOR_1, ACCUMULATOR_2, GET_AGENT_AUTHZ, GET_AGENT_AUTHZ_ACCUM_WIT
from indy_node.server.plugin.agent_authz.messages.fields import \
    AgentAuthzPolicyAddressField, AgentAuthzCommitmentField, \
    AgentAuthzAuthorisationField, AgentAuthzAccumIdField
from plenum.common.constants import TXN_TYPE, VERKEY
from plenum.common.messages.fields import ConstantField, FullVerkeyField
from plenum.common.messages.message_base import MessageValidator


# Temporary value, needs to change
MAX_POLICY_ADDRESS = 92320714731731605140513965263293775136553351682923655920670851703544265531624000000
# Temporary value, needs to change
MAX_COMMITMENT = 318028647963126151329853788044970037553383723548483991111562082327990638642710893355904748171562443528303700560839933521244978396415095418730498962422748911233060199731345351794902617682381377504128982684873285344278700181318498672093457626984884328901609908211755665042560103660590284040739154480985634957587000000


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
        (TXN_TYPE, ConstantField(GET_AGENT_AUTHZ)),
        (ADDRESS, AgentAuthzPolicyAddressField(MAX_POLICY_ADDRESS)),
    )


class ClientAgentAuthzAccumWitGetOperation(MessageValidator):
    schema = (
        (TXN_TYPE, ConstantField(GET_AGENT_AUTHZ_ACCUM_WIT)),
        (ACCUMULATOR_ID, AgentAuthzAccumIdField(ACCUMULATOR_1, ACCUMULATOR_2)),
        (COMMITMENT, AgentAuthzCommitmentField(MAX_COMMITMENT)),
    )
