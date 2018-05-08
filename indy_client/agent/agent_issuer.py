import json
from plenum.common.types import f

from anoncreds.protocol.issuer import Issuer
from anoncreds.protocol.types import ID
from anoncreds.protocol.types import ClaimRequest
from indy_client.agent.constants import EVENT_NOTIFY_MSG, CLAIMS_LIST_FIELD
from indy_client.agent.msg_constants import CLAIM, CLAIM_REQ_FIELD, CLAIM_FIELD, \
    AVAIL_CLAIM_LIST, REVOC_REG_SEQ_NO, SCHEMA_SEQ_NO, ISSUER_DID
from indy_common.identity import Identity
from plenum.common.constants import DATA
from indy_client.client.wallet.attribute import Attribute


class AgentIssuer:
    def __init__(self, issuer: Issuer):
        self.issuer = issuer

    async def processReqAvailClaims(self, msg):
        body, (frm, ha) = msg
        link = self.verifyAndGetLink(msg)
        data = {
            CLAIMS_LIST_FIELD: self.get_available_claim_list(link)
        }
        resp = self.getCommonMsg(AVAIL_CLAIM_LIST, data)
        self.signAndSend(resp, link.localIdentifier, frm)

    async def processReqClaim(self, msg):
        body, (frm, _) = msg
        link = self.verifyAndGetLink(msg)
        if not link:
            raise NotImplementedError

        claimReqDetails = body[DATA]

        schemaId = ID(schemaId=claimReqDetails[SCHEMA_SEQ_NO])
        schema = await self.issuer.wallet.getSchema(schemaId)

        if not self.is_claim_available(link, schema.name):
            self.notifyToRemoteCaller(
                EVENT_NOTIFY_MSG, "This claim is not yet available.",
                self.wallet.defaultId, frm,
                origReqId=body.get(f.REQ_ID.nm))
            return

        public_key = await self.issuer.wallet.getPublicKey(schemaId)
        claimReq = ClaimRequest.from_str_dict(
            claimReqDetails[CLAIM_REQ_FIELD], public_key.N)

        self._add_attribute(
            schemaKey=schema.getKey(),
            proverId=claimReq.userId,
            link=link)

        claim_signature, claim_attributes = await self.issuer.issueClaim(schemaId, claimReq)

        claimDetails = {
            f.SIG.nm: claim_signature.to_str_dict(),
            ISSUER_DID: schema.issuerId,
            CLAIM_FIELD: json.dumps({k: v.to_str_dict() for k, v in claim_attributes.items()}),
            REVOC_REG_SEQ_NO: None,
            SCHEMA_SEQ_NO: claimReqDetails[SCHEMA_SEQ_NO]
        }

        resp = self.getCommonMsg(CLAIM, claimDetails)
        self.signAndSend(resp, link.localIdentifier, frm,
                         origReqId=body.get(f.REQ_ID.nm))

    def _add_attribute(self, schemaKey, proverId, link):
        attr = self.issuer_backend.get_record_by_internal_id(link.internalId)
        self.issuer._attrRepo.addAttributes(schemaKey=schemaKey,
                                            userId=proverId,
                                            attributes=attr)

    def publish_trust_anchor(self, idy: Identity):
        self.wallet.addTrustAnchoredIdentity(idy)
        reqs = self.wallet.preparePending()
        self.client.submitReqs(*reqs)

    def publish_trust_anchor_attribute(self, attrib: Attribute):
        self.wallet.addAttribute(attrib)
        reqs = self.wallet.preparePending()
        self.client.submitReqs(*reqs)
