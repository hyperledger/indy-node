from indy_node.server.plugin.agent_authz.domain_req_handler import \
    DomainReqHandlerWithAuthz
from plenum.server.client_authn import CoreAuthNr


class AgentAuthzAuthNr(CoreAuthNr):
    write_types = CoreAuthNr.write_types.union(
        DomainReqHandlerWithAuthz.write_types)
    query_types = CoreAuthNr.query_types.union(
        DomainReqHandlerWithAuthz.query_types)

    def __init__(self, authz_cache):
        self.cache = authz_cache

    def getVerkey(self, identifier):
        if len(identifier) in (43, 44):
            # Address is the 32 byte verkey
            return identifier
