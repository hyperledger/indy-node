from typing import Any
from collections import OrderedDict

from plenum.common.constants import NAME, NONCE, TYPE, DATA, VERSION, \
    ATTRIBUTES, VERIFIABLE_ATTRIBUTES
from plenum.common.types import f

from anoncreds.protocol.types import FullProof
from anoncreds.protocol.types import ProofInput
from anoncreds.protocol.utils import fromDictWithStrValues
from anoncreds.protocol.verifier import Verifier
from sovrin_client.agent.msg_constants import PROOF_STATUS, PROOF_FIELD, \
    PROOF_INPUT_FIELD, REVEALED_ATTRS_FIELD, PROOF_REQUEST, \
    PROOF_REQ_SCHEMA_NAME, PROOF_REQ_SCHEMA_VERSION, \
    PROOF_REQ_SCHEMA_ATTRIBUTES, PROOF_REQ_SCHEMA_VERIFIABLE_ATTRIBUTES, \
    ERR_NO_PROOF_REQUEST_SCHEMA_FOUND
from sovrin_client.client.wallet.link import Link
from sovrin_common.util import getNonceForProof


class AgentVerifier(Verifier):
    def __init__(self, verifier: Verifier):
        self.verifier = verifier

    async def verifyProof(self, msg: Any):
        body, (frm, _) = msg
        link = self.verifyAndGetLink(msg)
        if not link:
            raise NotImplementedError

        proofName = body[NAME]
        nonce = getNonceForProof(body[NONCE])
        proof = FullProof.fromStrDict(body[PROOF_FIELD])
        proofInput = ProofInput.fromStrDict(body[PROOF_INPUT_FIELD])
        revealedAttrs = fromDictWithStrValues(body[REVEALED_ATTRS_FIELD])
        result = await self.verifier.verify(proofInput, proof,
                                            revealedAttrs, nonce)

        self.logger.info('Proof "{}" accepted with nonce {}'
                              .format(proofName, nonce))
        self.logger.info('Verifying proof "{}" from {}'
                              .format(proofName, link.name))
        status = 'verified' if result else 'failed verification'
        resp = {
            TYPE: PROOF_STATUS,
            DATA: '    Your Proof {} {} was received and {}\n'.
                format(body[NAME], body[VERSION], status),
        }
        self.signAndSend(resp, link.localIdentifier, frm,
                         origReqId=body.get(f.REQ_ID.nm))

        if result:
            for attribute in proofInput.revealedAttrs:
                # Log attributes that were verified
                self.logger.info('verified {}: {}'.
                                 format(attribute, revealedAttrs[attribute]))
            self.logger.info('Verified that proof "{}" contains attributes '
                             'from claim(s) issued by: {}'.format(
                proofName, ", ".join(
                    sorted([sk.issuerId for sk in proof.schemaKeys]))))
            await self._postProofVerif(proofName, link, frm)
        else:
            self.logger.info('Verification failed for proof {} from {} '
                              .format(proofName, link.name))

    def sendProofReq(self, link: Link, proofReqSchemaKey):
        if self._proofRequestsSchema and (
                    proofReqSchemaKey in self._proofRequestsSchema):
            proofRequest = self._proofRequestsSchema[proofReqSchemaKey]
            op = OrderedDict([
                (TYPE, PROOF_REQUEST),
                (NAME, proofRequest[PROOF_REQ_SCHEMA_NAME]),
                (VERSION, proofRequest[PROOF_REQ_SCHEMA_VERSION]),
                (ATTRIBUTES, proofRequest[PROOF_REQ_SCHEMA_ATTRIBUTES]),
                (VERIFIABLE_ATTRIBUTES,
                 proofRequest[PROOF_REQ_SCHEMA_VERIFIABLE_ATTRIBUTES])
            ])

            self.signAndSendToLink(msg=op, linkName=link.name)
        else:
            return ERR_NO_PROOF_REQUEST_SCHEMA_FOUND
