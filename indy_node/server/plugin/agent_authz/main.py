from indy_node.server.plugin.agent_authz.client_authnr import AgentAuthzAuthNr
from indy_node.server.plugin.agent_authz.config import get_config
from indy_node.server.plugin.agent_authz.domain_req_handler import \
    DomainReqHandlerWithAuthz
from indy_node.server.plugin.agent_authz.storage import \
    get_authz_commitment_cache, get_commitment_db_accum
from plenum.common.constants import DOMAIN_LEDGER_ID


def integrate_plugin_in_node(node):
    node.config = get_config(node.config)
    authz_cache = get_authz_commitment_cache(node.dataLocation,
                                             node.config.AgentAuthzCommitmentCacheDbName,
                                             node.config)
    commitment_db1 = get_commitment_db_accum(node.dataLocation,
                                             node.config.AgentAuthzAccum1CommDbName, node.config)
    commitment_db2 = get_commitment_db_accum(node.dataLocation,
                                             node.config.AgentAuthzAccum2CommDbName,
                                             node.config)
    domain_req_handler = node.get_req_handler(ledger_id=DOMAIN_LEDGER_ID)
    domain_state = node.getState(DOMAIN_LEDGER_ID)
    authz_req_handler = DomainReqHandlerWithAuthz(domain_state=domain_state,
                                                  cache=authz_cache,
                                                  commitment_db1=commitment_db1,
                                                  commitment_db2=commitment_db2,
                                                  config=node.config)
    authz_req_handler.update_req_handler(domain_req_handler)
    for txn_type in authz_req_handler.valid_txn_types:
        node.register_txn_type(txn_type, DOMAIN_LEDGER_ID, domain_req_handler)
    authz_req_handler.add_hooks(node)
    agent_authnr = AgentAuthzAuthNr(authz_cache)
    node.clientAuthNr.register_authenticator(agent_authnr)
    return node
