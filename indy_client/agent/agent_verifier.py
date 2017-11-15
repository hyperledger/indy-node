from typing import Any

from plenum.common.constants import NAME, NONCE, TYPE, DATA, VERSION, \
    ATTRIBUTES, VERIFIABLE_ATTRIBUTES, PREDICATES
from plenum.common.types import f

from anoncreds.protocol.types import FullProof, ProofInfo, ID, AggregatedProof, RequestedProof
from anoncreds.protocol.types import ProofRequest
from anoncreds.protocol.verifier import Verifier
from indy_client.agent.msg_constants import PROOF_STATUS, PROOF_FIELD, PROOF_REQUEST, \
    PROOF_REQUEST_FIELD, ERR_NO_PROOF_REQUEST_SCHEMA_FOUND
from indy_client.client.wallet.connection import Connection
from indy_common.util import getNonceForProof


class AgentVerifier(Verifier):
    def __init__(self, verifier: Verifier):
        self.verifier = verifier

    async def verifyProof(self, msg: Any):
        body, (frm, _) = msg
        link = self.verifyAndGetLink(msg)
        if not link:
            raise NotImplementedError

        proof = body[PROOF_FIELD]
        proofRequest = ProofRequest.from_str_dict(body[PROOF_REQUEST_FIELD])
        nonce = getNonceForProof(body[NONCE])
        proofName = proofRequest.name

        proofs = {}

        for key, p in proof['proofs'].items():
            schema = await self.verifier.wallet.getSchema(ID(schemaId=int(p['schema_seq_no'])))
            pk = await self.verifier.wallet.getPublicKey(ID(schemaKey=schema.getKey()))
            proofs[key] = ProofInfo.from_str_dict(p, str(pk.N))

        proof = FullProof(
            proofs, AggregatedProof.from_str_dict(
                proof['aggregated_proof']), RequestedProof.from_str_dict(
                proof['requested_proof']))

        result = await self.verifier.verify(proofRequest, proof)

        self.logger.info('Proof "{}" accepted with nonce {}'
                         .format(proofName, nonce))
        self.logger.info('Verifying proof "{}" from {}'
                         .format(proofName, link.name))
        status = 'verified' if result else 'failed verification'
        resp = {
            TYPE: PROOF_STATUS,
            DATA: '    Your Proof {} {} was received and {}\n'.
            format(proofRequest.name, proofRequest.version, status),
        }
        self.signAndSend(resp, link.localIdentifier, frm,
                         origReqId=body.get(f.REQ_ID.nm))

        if result:
            for uuid, attribute in proofRequest.verifiableAttributes.items():
                # Log attributes that were verified
                self.logger.info(
                    'verified {}: {}'. format(
                        attribute.name,
                        proof.requestedProof.revealed_attrs[uuid][1]))
            self.logger.info('Verified that proof "{}" contains attributes '
                             'from claim(s) issued by: {}'.format(
                                 proofName, ", ".join(
                                     sorted([v.issuer_did for k, v in proof.proofs.items()]))))
            await self._postProofVerif(proofName, link, frm)
        else:
            self.logger.info('Verification failed for proof {} from {} '
                             .format(proofName, link.name))

    def sendProofReq(self, link: Connection, proofReqSchemaKey):
        if self._proofRequestsSchema and (
                proofReqSchemaKey in self._proofRequestsSchema):
            proofRequest = self._proofRequestsSchema[proofReqSchemaKey]

            proofRequest = ProofRequest(
                proofRequest[NAME],
                proofRequest[VERSION],
                getNonceForProof(link.request_nonce),
                proofRequest[ATTRIBUTES],
                proofRequest[VERIFIABLE_ATTRIBUTES] if VERIFIABLE_ATTRIBUTES in proofRequest else [
                ],
                proofRequest[PREDICATES] if PREDICATES in proofRequest else []
            )

            op = {
                TYPE: PROOF_REQUEST,
                PROOF_REQUEST_FIELD: proofRequest.to_str_dict()
            }

            self.signAndSendToLink(msg=op, linkName=link.name)
        else:
            return ERR_NO_PROOF_REQUEST_SCHEMA_FOUND
