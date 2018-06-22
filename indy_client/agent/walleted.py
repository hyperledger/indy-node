import asyncio
import collections
import inspect
import json
import time
from datetime import datetime
from typing import Dict, List, Union

from base58 import b58decode
from common.serializers.serialization import serialize_msg_for_signing

from stp_core.common.log import getlogger
from plenum.common.signer_did import DidSigner
from plenum.common.constants import TYPE, DATA, NONCE, IDENTIFIER, NAME, VERSION, \
    TARGET_NYM, ATTRIBUTES, VERKEY, VERIFIABLE_ATTRIBUTES, PREDICATES
from plenum.common.types import f
from plenum.common.util import getTimeBasedId, getCryptonym, \
    isMaxCheckTimeExpired, convertTimeBasedReqIdToMillis, friendlyToRaw
from plenum.common.verifier import DidVerifier

from anoncreds.protocol.issuer import Issuer
from anoncreds.protocol.prover import Prover
from anoncreds.protocol.verifier import Verifier
from anoncreds.protocol.globals import TYPE_CL
from anoncreds.protocol.types import AttribDef, ID, ProofRequest, AvailableClaim
from plenum.common.exceptions import NotConnectedToAny
from indy_client.agent.agent_issuer import AgentIssuer
from indy_client.agent.backend import BackendSystem
from indy_client.agent.agent_prover import AgentProver
from indy_client.agent.agent_verifier import AgentVerifier
from indy_client.agent.constants import ALREADY_ACCEPTED_FIELD, CLAIMS_LIST_FIELD, \
    REQ_MSG, PING, ERROR, EVENT, EVENT_NAME, EVENT_NOTIFY_MSG, \
    EVENT_POST_ACCEPT_INVITE, PONG, EVENT_NOT_CONNECTED_TO_ANY_ENV
from indy_client.agent.exception import NonceNotFound, SignatureRejected
from indy_client.agent.helper import friendlyVerkeyToPubkey, rawVerkeyToPubkey
from indy_client.agent.msg_constants import ACCEPT_INVITE, CLAIM_REQUEST, \
    PROOF, AVAIL_CLAIM_LIST, CLAIM, PROOF_STATUS, NEW_AVAILABLE_CLAIMS, \
    REF_REQUEST_ID, REQ_AVAIL_CLAIMS, INVITE_ACCEPTED, PROOF_REQUEST
from indy_client.client.wallet.attribute import Attribute, LedgerStore
from indy_client.client.wallet.connection import Connection, constant
from indy_client.client.wallet.wallet import Wallet
from indy_common.exceptions import ConnectionNotFound, ConnectionAlreadyExists, \
    NotConnectedToNetwork, LinkNotReady, VerkeyNotFound, RemoteEndpointNotFound
from indy_common.identity import Identity
from indy_common.constants import ENDPOINT
from indy_common.util import ensureReqCompleted
from indy_common.config import agentLoggingLevel
from indy_common.exceptions import InvalidConnectionException
from plenum.common.constants import PUBKEY
from indy_common.util import getNonceForProof

logger = getlogger()
logger.setLevel(agentLoggingLevel)


class Walleted(AgentIssuer, AgentProver, AgentVerifier):
    """
    An agent with a self-contained wallet.

    Normally, other logic acts upon a remote agent. That other logic holds keys
    and signs messages and transactions that the Agent then forwards. In this
    case, the agent holds a wallet.
    """

    def __init__(self,
                 issuer: Issuer = None,
                 prover: Prover = None,
                 verifier: Verifier = None):

        AgentIssuer.__init__(self, issuer)
        AgentProver.__init__(self, prover)
        AgentVerifier.__init__(self, verifier)

        # TODO Why are we syncing the client here?
        if self.client:
            self.syncClient()
        self.rcvdMsgStore = {}  # type: Dict[reqId, [reqMsg]]

        self.msgHandlers = {
            ERROR: self._handleError,
            EVENT: self._eventHandler,

            PING: self._handlePing,
            ACCEPT_INVITE: self._handleAcceptance,
            REQ_AVAIL_CLAIMS: self.processReqAvailClaims,

            CLAIM_REQUEST: self.processReqClaim,
            CLAIM: self.handleReqClaimResponse,

            PROOF: self.verifyProof,
            PROOF_STATUS: self.handleProofStatusResponse,
            PROOF_REQUEST: self.handleProofRequest,

            PONG: self._handlePong,
            INVITE_ACCEPTED: self._handleAcceptInviteResponse,
            AVAIL_CLAIM_LIST: self._handleAvailableClaimsResponse,

            NEW_AVAILABLE_CLAIMS: self._handleNewAvailableClaimsDataResponse
        }
        self.logger = logger

        self.issuer_backend = None

        self._invites = {}  # type: Dict[Nonce, Tuple(InternalId, str)]
        self._attribDefs = {}  # type: Dict[str, AttribDef]
        self.defined_claims = []  # type: List[Dict[str, Any]

        # dict for proof request schema Dict[str, Dict[str, any]]
        self._proofRequestsSchema = {}

    def syncClient(self):
        obs = self._wallet.handleIncomingReply
        if not self.client.hasObserver(obs):
            self.client.registerObserver(obs)
        self._wallet.pendSyncRequests()
        prepared = self._wallet.preparePending()
        self.client.submitReqs(*prepared)

    @property
    def wallet(self) -> Wallet:
        return self._wallet

    @wallet.setter
    def wallet(self, wallet):
        self._wallet = wallet

    @property
    def lockedMsgs(self):
        # Msgs for which signature verification is required
        return ACCEPT_INVITE, CLAIM_REQUEST, PROOF, \
            CLAIM, AVAIL_CLAIM_LIST, EVENT, PONG, REQ_AVAIL_CLAIMS

    async def postProofVerif(self, claimName, link, frm):
        raise NotImplementedError

    def is_claim_available(self, link, claim_name):
        return any(
            ac[NAME] == claim_name for ac in self._get_available_claim_list_by_internal_id(
                link.internalId))

    async def _postProofVerif(self, claimName, link, frm):
        link.verifiedClaimProofs.append(claimName)
        await self.postProofVerif(claimName, link, frm)

    async def _set_available_claim_by_internal_id(self, internal_id, schema_id):
        sd = await self.schema_dict_from_id(schema_id)
        try:
            if not any(
                    d == sd for d in self.issuer.wallet.availableClaimsByInternalId[internal_id]):
                self.issuer.wallet.availableClaimsByInternalId[internal_id].append(
                    sd)
        except KeyError:
            self.issuer.wallet.availableClaimsByInternalId[internal_id] = [sd]

    def _get_available_claim_list_by_internal_id(self, internal_id):
        return self.issuer.wallet.availableClaimsByInternalId.get(
            internal_id, set())

    def get_available_claim_list(self, link):
        li = self.wallet.getConnectionBy(remote=link.remoteIdentifier)
        # TODO: Need to return set instead of list, but if we return set,
        # stack communication fails as set is not json serializable,
        # need to work on that.
        if li is None:
            return list()
        return list(
            self._get_available_claim_list_by_internal_id(li.internalId))

    def getErrorResponse(self, reqBody, errorMsg="Error"):
        invalidSigResp = {
            TYPE: ERROR,
            DATA: errorMsg,
            REQ_MSG: reqBody,
        }
        return invalidSigResp

    def logAndSendErrorResp(self, to, reqBody, respMsg, logMsg):
        logger.warning(logMsg)
        self.signAndSend(msg=self.getErrorResponse(reqBody, respMsg),
                         signingIdr=self.wallet.defaultId, name=to)

    # TODO: Verification needs to be moved out of it,
    # use `verifySignature` instead
    def verifyAndGetLink(self, msg):
        body, (frm, ha) = msg
        nonce = body.get(NONCE)
        try:
            kwargs = dict(nonce=nonce, remoteIdr=body.get(
                f.IDENTIFIER.nm), remoteHa=ha)
            if ha is None:
                # Incase of ZStack,
                kwargs.update(remotePubkey=frm)
            return self.linkFromNonce(**kwargs)
        except NonceNotFound:
            self.logAndSendErrorResp(frm, body,
                                     "Nonce not found",
                                     "Nonce not found for msg: {}".format(msg))
            return None

    def linkFromNonce(self, nonce, remoteIdr, remoteHa=None,
                      remotePubkey=None):
        internalId = self.get_internal_id_by_nonce(nonce)
        linkName = self.get_link_name_by_internal_id(internalId)
        link = self.wallet.getConnectionBy(internalId=internalId)
        if not link:
            # QUESTION: We use wallet.defaultId as the local identifier,
            # this looks ok for test code, but not production code
            link = Connection(linkName,
                              self.wallet.defaultId,
                              self.wallet.getVerkey(),
                              request_nonce=nonce,
                              remoteIdentifier=remoteIdr,
                              remoteEndPoint=remoteHa,
                              internalId=internalId,
                              remotePubkey=remotePubkey)
            self.wallet.addConnection(link)
        else:
            link.remoteIdentifier = remoteIdr
            link.remoteEndPoint = remoteHa
        return link

    def get_internal_id_by_nonce(self, nonce):
        if nonce in self._invites:
            return self._invites[nonce][0]
        else:
            raise NonceNotFound

    def get_link_name_by_internal_id(self, internalId):
        for invite in self._invites.values():
            if invite[0] == internalId:
                return invite[1]

    def set_issuer_backend(self, backend: BackendSystem):
        self.issuer_backend = backend

    async def publish_issuer_keys(self, schema_id, p_prime, q_prime):
        keys = await self.issuer.genKeys(schema_id,
                                         p_prime=p_prime,
                                         q_prime=q_prime)
        await self.add_to_available_claims(schema_id)
        return keys

    async def schema_dict_from_id(self, schema_id):
        schema = await self.issuer.wallet.getSchema(schema_id)
        return self.schema_dict(schema)

    async def publish_revocation_registry(self, schema_id, rev_reg_id='110', size=5):
        return await self.issuer.issueAccumulator(schemaId=schema_id,
                                                  iA=rev_reg_id,
                                                  L=size)

    def schema_dict(self, schema):
        return {
            NAME: schema.name,
            VERSION: schema.version,
            "schemaSeqNo": schema.seqId
        }

    async def add_to_available_claims(self, schema_id):
        schema = await self.issuer.wallet.getSchema(schema_id)
        self.defined_claims.append(self.schema_dict(schema))

    async def publish_schema(self,
                             attrib_def_name,
                             schema_name,
                             schema_version):
        attribDef = self._attribDefs[attrib_def_name]
        schema = await self.issuer.genSchema(schema_name,
                                             schema_version,
                                             attribDef.attribNames())
        schema_id = ID(schemaKey=schema.getKey(), schemaId=schema.seqId)
        return schema_id

    def add_attribute_definition(self, attr_def: AttribDef):
        self._attribDefs[attr_def.name] = attr_def

    async def get_claim(self, schema_id: ID):
        return await self.prover.wallet.getClaimAttributes(schema_id)

    def new_identifier(self, seed=None):
        idr, _ = self.wallet.addIdentifier(seed=seed)
        verkey = self.wallet.getVerkey(idr)
        return idr, verkey

    def get_link_by_name(self, name):
        return self.wallet.getConnection(str(name))

    def signAndSendToLink(self, msg, linkName, origReqId=None):
        link = self.wallet.getConnection(linkName, required=True)
        if not link.localIdentifier:
            raise LinkNotReady('connection is not yet established, '
                               'send/accept request first')

        ha = link.getRemoteEndpoint(required=False)
        name = link.name
        if not ha:
            # if not remote address is present, then it's upcominh link, so we may have no
            # explicit connection (wrk in a listener mode).
            # PulicKey is used as a name in this case
            name = link.remotePubkey

        if ha:
            self.connectTo(link=link)

        return self.signAndSend(msg=msg, signingIdr=link.localIdentifier,
                                name=name, ha=ha, origReqId=origReqId)

    def signAndSend(self, msg, signingIdr, name=None, ha=None, origReqId=None):
        msg[f.REQ_ID.nm] = getTimeBasedId()
        if origReqId:
            msg[REF_REQUEST_ID] = origReqId

        msg[IDENTIFIER] = signingIdr
        signature = self.wallet.signMsg(msg, signingIdr)
        msg[f.SIG.nm] = signature

        self.sendMessage(msg, name=name, ha=ha)

        return msg[f.REQ_ID.nm]

    @staticmethod
    def getCommonMsg(typ, data):
        msg = {
            TYPE: typ,
            DATA: data
        }
        return msg

    @classmethod
    def createInviteAcceptedMsg(cls, claimLists, alreadyAccepted=False):
        data = {
            CLAIMS_LIST_FIELD: claimLists
        }
        if alreadyAccepted:
            data[ALREADY_ACCEPTED_FIELD] = alreadyAccepted

        return cls.getCommonMsg(INVITE_ACCEPTED, data)

    @classmethod
    def createNewAvailableClaimsMsg(cls, claimLists):
        data = {
            CLAIMS_LIST_FIELD: claimLists
        }
        return cls.getCommonMsg(NEW_AVAILABLE_CLAIMS, data)

    @classmethod
    def createClaimMsg(cls, claim):
        return cls.getCommonMsg(CLAIM, claim)

    def _eventHandler(self, msg):
        body, _ = msg
        eventName = body[EVENT_NAME]
        data = body[DATA]
        self.notifyEventListeners(eventName, **data)

    def notifyEventListeners(self, eventName, **data):
        for el in self._eventListeners.get(eventName, []):
            el(notifier=self, **data)

    def notifyMsgListener(self, msg):
        self.notifyEventListeners(EVENT_NOTIFY_MSG, msg=msg)

    def isSignatureVerifRespRequired(self, typ):
        return typ in self.lockedMsgs and typ not in [EVENT, PING, PONG]

    def sendSigVerifResponseMsg(self, respMsg, to, reqMsgTyp, identifier):
        if self.isSignatureVerifRespRequired(reqMsgTyp):
            self.notifyToRemoteCaller(EVENT_NOTIFY_MSG,
                                      respMsg, identifier, to)

    def handleEndpointMessage(self, msg):
        body, frm = msg
        logger.debug("Message received (from -> {}): {}".format(frm, body))
        if isinstance(frm, bytes):
            frm = frm.decode()
        for reqFieldName in (TYPE, f.REQ_ID.nm):
            reqFieldValue = body.get(reqFieldName)
            if not reqFieldValue:
                errorMsg = "{} not specified in message: {}".format(
                    reqFieldName, body)
                self.notifyToRemoteCaller(EVENT_NOTIFY_MSG,
                                          errorMsg, self.wallet.defaultId, frm)
                logger.warning("{}".format(errorMsg))
                return

        typ = body.get(TYPE)
        link = self.wallet.getConnectionBy(remote=body.get(f.IDENTIFIER.nm))

        # If accept invite is coming the first time, then use the default
        # identifier of the wallet since link wont be created
        if typ == ACCEPT_INVITE and link is None:
            localIdr = self.wallet.defaultId
        else:
            # if accept invite is not the message type
            # and we are still missing link, then return the error
            if link is None:
                linkNotCreated = '    Error processing {}. ' \
                                 'Connection is not yet created.'.format(typ)
                self.notifyToRemoteCaller(EVENT_NOTIFY_MSG,
                                          linkNotCreated,
                                          self.wallet.defaultId,
                                          frm)
                return

            localIdr = link.localIdentifier

        if typ in self.lockedMsgs:
            try:
                self.verifySignature(body)
            except SignatureRejected:
                self.sendSigVerifResponseMsg("\nSignature rejected.",
                                             frm, typ, localIdr)
                return
        reqId = body.get(f.REQ_ID.nm)

        oldResps = self.rcvdMsgStore.get(reqId)
        if oldResps:
            oldResps.append(msg)
        else:
            self.rcvdMsgStore[reqId] = [msg]

        # TODO: Question: Should we sending an acknowledgement for every message?
        # We are sending, ACKs for "signature accepted" messages too
        self.sendSigVerifResponseMsg("\nSignature accepted.",
                                     frm, typ, localIdr)

        handler = self.msgHandlers.get(typ)
        if handler:
            # TODO we should verify signature here
            frmHa = self.endpoint.getHa(frm)
            # `frmHa` can be None
            res = handler((body, (frm, frmHa)))
            if inspect.isawaitable(res):
                self.loop.call_soon(asyncio.ensure_future, res)
        else:
            raise NotImplementedError("No type handle found for {} message".
                                      format(typ))

    def _handleError(self, msg):
        body, _ = msg
        self.notifyMsgListener("Error ({}) occurred while processing this "
                               "msg: {}".format(body[DATA], body[REQ_MSG]))

    def _handlePing(self, msg):
        body, (frm, ha) = msg
        link = self.wallet.getConnectionBy(nonce=body.get(NONCE))
        if link:
            self.logger.info('Ping sent to %s', link.remoteIdentifier)
            self.signAndSend({TYPE: 'pong'}, self.wallet.defaultId, frm,
                             origReqId=body.get(f.REQ_ID.nm))

    def _handlePong(self, msg):
        body, (frm, ha) = msg
        identifier = body.get(IDENTIFIER)
        if identifier:
            li = self._getLinkByTarget(getCryptonym(identifier))
            if li:
                self.logger.info('Pong received from %s', li.remoteIdentifier)
                self.notifyMsgListener("    Pong received.")
            else:
                self.notifyMsgListener(
                    "    Pong received from unknown endpoint.")
        else:
            self.notifyMsgListener('    Identifier is not yet set.')

    def _handleNewAvailableClaimsDataResponse(self, msg):
        body, _ = msg
        isVerified = self.verifySignature(body)
        if isVerified:
            identifier = body.get(IDENTIFIER)
            li = self._getLinkByTarget(getCryptonym(identifier))
            if li:
                self.notifyResponseFromMsg(li.name, body.get(f.REQ_ID.nm))

                rcvdAvailableClaims = body[DATA][CLAIMS_LIST_FIELD]
                newAvailableClaims = self._getNewAvailableClaims(
                    li, rcvdAvailableClaims)
                if newAvailableClaims:
                    li.availableClaims.extend(newAvailableClaims)
                    claimNames = ", ".join(
                        [n for n, _, _ in newAvailableClaims])
                    self.notifyMsgListener(
                        "    Available Claim(s): {}\n".format(claimNames))

            else:
                self.notifyMsgListener("No matching connection found")

    @staticmethod
    def _getNewAvailableClaims(
            li, rcvdAvailableClaims) -> List[AvailableClaim]:
        receivedClaims = [AvailableClaim(cl[NAME],
                                         cl[VERSION],
                                         li.remoteIdentifier)
                          for cl in rcvdAvailableClaims]
        existingAvailableClaims = set(li.availableClaims)
        newReceivedClaims = set(receivedClaims)
        return list(newReceivedClaims - existingAvailableClaims)

    def _handleAvailableClaimsResponse(self, msg):
        body, _ = msg
        identifier = body.get(IDENTIFIER)
        li = self._getLinkByTarget(getCryptonym(identifier))
        if li:
            rcvdAvailableClaims = body[DATA][CLAIMS_LIST_FIELD]
            if len(rcvdAvailableClaims) > 0:
                self.notifyMsgListener("    Available Claim(s): {}". format(
                    ",".join([rc.get(NAME) for rc in rcvdAvailableClaims])))
            else:
                self.notifyMsgListener("    Available Claim(s): "
                                       "No available claims found")

    def _handleAcceptInviteResponse(self, msg):
        body, _ = msg
        identifier = body.get(IDENTIFIER)
        li = self._getLinkByTarget(getCryptonym(identifier))
        if li:
            # TODO: Show seconds took to respond
            self.notifyResponseFromMsg(li.name, body.get(f.REQ_ID.nm))
            self.notifyMsgListener("    Trust established.")
            alreadyAccepted = body[DATA].get(ALREADY_ACCEPTED_FIELD)
            if alreadyAccepted:
                self.notifyMsgListener("    Already accepted.")
            else:
                self.notifyMsgListener("    DID created in Indy.")

                li.connection_status = constant.CONNECTION_STATUS_ACCEPTED
                rcvdAvailableClaims = body[DATA][CLAIMS_LIST_FIELD]
                newAvailableClaims = self._getNewAvailableClaims(
                    li, rcvdAvailableClaims)
                if newAvailableClaims:
                    li.availableClaims.extend(newAvailableClaims)
                    self.notifyMsgListener("    Available Claim(s): {}". format(
                        ",".join([rc.get(NAME) for rc in rcvdAvailableClaims])))
                try:
                    self._checkIfLinkIdentifierWrittenToIndy(
                        li, newAvailableClaims)
                except NotConnectedToAny:
                    self.notifyEventListeners(
                        EVENT_NOT_CONNECTED_TO_ANY_ENV,
                        msg="Cannot check if identifier is written to Indy.")
        else:
            self.notifyMsgListener("No matching connection found")

    def getVerkeyForLink(self, link):
        # TODO: Get latest verkey for this link's remote identifier from Indy
        if link.remoteVerkey:
            return link.remoteVerkey
        else:
            raise VerkeyNotFound("verkey not set in connection")

    def getLinkForMsg(self, msg):
        nonce = msg.get(NONCE)
        identifier = msg.get(f.IDENTIFIER.nm)
        link = self.wallet.getConnectionBy(nonce=nonce, remote=identifier)
        if link:
            return link
        else:
            raise ConnectionNotFound

    def verifySignature(self, msg: Dict[str, str]):
        signature = msg.get(f.SIG.nm)
        identifier = msg.get(IDENTIFIER)
        msgWithoutSig = {k: v for k, v in msg.items() if k != f.SIG.nm}
        # TODO This assumes the current key is the cryptonym. This is a BAD
        # ASSUMPTION!!! Indy needs to provide the current key.
        ser = serialize_msg_for_signing(msgWithoutSig)
        signature = b58decode(signature.encode())
        typ = msg.get(TYPE)
        # TODO: Maybe keeping ACCEPT_INVITE open is a better option than keeping
        # an if condition here?
        if typ == ACCEPT_INVITE:
            verkey = msg.get(VERKEY)
        else:
            try:
                link = self.getLinkForMsg(msg)
                verkey = self.getVerkeyForLink(link)
            except (ConnectionNotFound, VerkeyNotFound):
                # This is for verification of `NOTIFY` events
                link = self.wallet.getConnectionBy(remote=identifier)
                # TODO: If verkey is None, it should be fetched from Indy.
                # Assuming CID for now.
                verkey = link.remoteVerkey

        v = DidVerifier(verkey, identifier=identifier)
        if not v.verify(signature, ser):
            raise SignatureRejected
        else:
            if typ == ACCEPT_INVITE:
                self.logger.info('Signature accepted.')
            return True

    def _getLinkByTarget(self, target) -> Connection:
        return self.wallet.getConnectionBy(remote=target)

    def _checkIfLinkIdentifierWrittenToIndy(
            self, li: Connection, availableClaims):
        req = self.getIdentity(li.localIdentifier)
        self.notifyMsgListener("\nSynchronizing...")

        def getNymReply(reply, err, availableClaims, li: Connection):
            if reply.get(DATA) and json.loads(reply[DATA])[TARGET_NYM] == \
                    li.localIdentifier:
                self.notifyMsgListener(
                    "    Confirmed DID written to Indy.")
                self.notifyEventListeners(
                    EVENT_POST_ACCEPT_INVITE, connection=li)
            else:
                self.notifyMsgListener(
                    "    DID is not yet written to Indy")

        self.loop.call_later(.2, ensureReqCompleted, self.loop,
                             (req.identifier, req.reqId),
                             self.client, getNymReply, (availableClaims, li))

    def notifyResponseFromMsg(self, linkName, reqId=None):
        if reqId:
            # TODO: This logic assumes that the req id is time based
            curTimeBasedId = getTimeBasedId()
            timeTakenInMillis = convertTimeBasedReqIdToMillis(
                curTimeBasedId - reqId)

            if timeTakenInMillis >= 1000:
                responseTime = ' ({} sec)'.format(
                    round(timeTakenInMillis / 1000, 2))
            else:
                responseTime = ' ({} ms)'.format(round(timeTakenInMillis, 2))
        else:
            responseTime = ''

        self.notifyMsgListener("\nResponse from {}{}:".format(linkName,
                                                              responseTime))

    def notifyToRemoteCaller(self, event, msg, signingIdr, to, origReqId=None):
        resp = {
            TYPE: EVENT,
            EVENT_NAME: event,
            DATA: {'msg': msg}
        }
        self.signAndSend(resp, signingIdr, to, origReqId=origReqId)

    def _handleAcceptance(self, msg):
        body, (frm, ha) = msg
        link = self.verifyAndGetLink(msg)
        # TODO this is really kludgy code... needs refactoring
        # exception handling, separation of concerns, etc.
        if not link:
            return
        logger.debug("proceeding with connection: {}".format(link.name))
        identifier = body.get(f.IDENTIFIER.nm)
        verkey = body.get(VERKEY)
        idy = Identity(identifier, verkey=verkey)
        link.remoteVerkey = verkey
        try:
            pendingCount = self.wallet.addTrustAnchoredIdentity(idy)
            logger.debug("pending request count {}".format(pendingCount))
            alreadyAdded = False
        except Exception as e:
            if e.args[0] in ['identifier already added']:
                alreadyAdded = True
            else:
                logger.warning("Exception raised while adding nym, "
                               "error was: {}".format(e.args[0]))
                raise e

        def send_claims(reply=None, error=None):
            return self.sendClaimList(link=link,
                                      alreadyAdded=alreadyAdded,
                                      sender=frm,
                                      reqId=body.get(f.REQ_ID.nm),
                                      reply=reply,
                                      error=error)

        if alreadyAdded:
            send_claims()
            logger.debug("already accepted, "
                         "so directly sending available claims")
            self.logger.info('Already added identifier [{}] in indy'
                             .format(identifier))
            # self.notifyToRemoteCaller(EVENT_NOTIFY_MSG,
            #                       "    Already accepted",
            #                       link.verkey, frm)
        else:
            logger.debug(
                "not added to the ledger, so add nym to the ledger "
                "and then will send available claims")
            reqs = self.wallet.preparePending()
            # Assuming there was only one pending request
            logger.debug("sending to indy {}".format(reqs[0]))
            # Need to think through
            # how to provide separate logging for each agent
            # anyhow this class should be implemented by each agent
            # so we might not even need to add it as a separate logic
            self.logger.info('Creating identifier [{}] in indy'
                             .format(identifier))
            self._sendToIndyAndDo(reqs[0], clbk=send_claims)

            # TODO: If I have the below exception thrown, somehow the
            # error msg which is sent in verifyAndGetLink is not being received
            # on the other end, so for now, commented, need to come back to this
            # else:
            #     raise NotImplementedError

    def sendClaimList(self, link, alreadyAdded, sender,
                      reqId, reply=None, error=None):
        logger.debug("sending available claims to {}".format(
            link.remoteIdentifier))
        resp = self.createInviteAcceptedMsg(
            self.get_available_claim_list(link),
            alreadyAccepted=alreadyAdded)
        self.signAndSend(resp, link.localIdentifier, sender,
                         origReqId=reqId)

    def _sendToIndyAndDo(self, req, clbk=None, *args, **kwargs):
        self.client.submitReqs(req)
        ensureReqCompleted(self.loop, (req.identifier, req.reqId),
                           self.client, clbk, *args, **kwargs)

    def newAvailableClaimsPostClaimVerif(self, claimName):
        raise NotImplementedError

    def sendNewAvailableClaimsData(self, nac, frm, link):
        if len(nac) > 0:
            resp = self.createNewAvailableClaimsMsg(nac)
            self.signAndSend(resp, link.localIdentifier, frm)

    def sendPing(self, linkName):
        link = self.wallet.getConnection(linkName, required=True)
        self.connectTo(link=link)
        ha = link.getRemoteEndpoint(required=True)
        params = dict(ha=ha)
        msg = {
            TYPE: 'ping',
            NONCE: link.request_nonce,
            f.REQ_ID.nm: getTimeBasedId(),
            f.IDENTIFIER.nm: link.localIdentifier
        }
        reqId = self.sendMessage(msg, **params)

        self.notifyMsgListener("    Ping sent.")
        return reqId

    def connectTo(self, linkName=None, link=None):
        assert linkName or link
        if link is None:
            link = self.wallet.getConnection(linkName, required=True)
        ha = link.getRemoteEndpoint(required=True)
        verKeyRaw = friendlyToRaw(
            link.full_remote_verkey) if link.full_remote_verkey else None
        publicKeyRaw = friendlyToRaw(
            link.remotePubkey) if link.remotePubkey else None

        if verKeyRaw is None and publicKeyRaw is None:
            raise InvalidConnectionException(
                "verkey or publicKey is required for connection.")

        if publicKeyRaw is None:
            publicKeyRaw = rawVerkeyToPubkey(verKeyRaw)
        self.endpoint.connectIfNotConnected(
            name=link.name,
            ha=ha,
            verKeyRaw=verKeyRaw,
            publicKeyRaw=publicKeyRaw)

    # duplicate function
    # def loadInvitationFile(self, filePath):
    #     with open(filePath) as data_file:
    #         request = json.load(
    #             data_file, object_pairs_hook=collections.OrderedDict)
    #         return self.load_request_dict(request)

    def load_request_str(self, json_str):
        request = json.loads(
            json_str, object_pairs_hook=collections.OrderedDict)
        return self.load_request_dict(request)

    def load_request_dict(self, request_dict):
        link_request = request_dict.get("connection-request")
        if not link_request:
            raise ConnectionNotFound
        linkName = link_request["name"]
        existingLinkInvites = self.wallet. \
            getMatchingConnections(linkName)
        if len(existingLinkInvites) >= 1:
            return self._merge_request(request_dict)
        Connection.validate(request_dict)
        link = self.load_request(request_dict)
        return link

    def load_request(self, request_data):
        link_request = request_data["connection-request"]
        remoteIdentifier = link_request[f.IDENTIFIER.nm]
        # TODO signature should be validated!
        # signature = request_data["sig"]
        link_request_name = link_request[NAME]
        remoteEndPoint = link_request.get("endpoint", None)
        remote_verkey = link_request.get("verkey", None)
        linkNonce = link_request[NONCE]
        proofRequestsJson = request_data.get("proof-requests", None)

        proofRequests = []
        if proofRequestsJson:
            for cr in proofRequestsJson:
                proofRequests.append(
                    ProofRequest(
                        cr[NAME],
                        cr[VERSION],
                        getNonceForProof(linkNonce),
                        cr[ATTRIBUTES],
                        cr[VERIFIABLE_ATTRIBUTES] if VERIFIABLE_ATTRIBUTES in cr else [],
                        cr[PREDICATES] if PREDICATES in cr else []))

        self.notifyMsgListener("1 connection request found for {}.".
                               format(link_request_name))

        self.notifyMsgListener("Creating connection for {}.".
                               format(link_request_name))
        # TODO: Would we always have a trust anchor corresponding to a link?

        li = Connection(name=link_request_name,
                        trustAnchor=link_request_name,
                        remoteIdentifier=remoteIdentifier,
                        remoteEndPoint=remoteEndPoint,
                        request_nonce=linkNonce,
                        proofRequests=proofRequests,
                        remote_verkey=remote_verkey)

        self.wallet.addConnection(li)
        return li

    def load_request_file(self, filePath):
        with open(filePath) as data_file:
            request_data = json.load(
                data_file, object_pairs_hook=collections.OrderedDict)
            link_request = request_data.get("connection-request")
            if not link_request:
                raise ConnectionNotFound
            linkName = link_request["name"]
            existingLinkInvites = self.wallet. \
                getMatchingConnections(linkName)
            if len(existingLinkInvites) >= 1:
                return self._merge_request(request_data)
            Connection.validate(request_data)
            link = self.load_request(request_data)
            return link

    def _merge_request(self, request_data):
        link_request = request_data.get('connection-request')
        linkName = link_request['name']
        link = self.wallet.getConnection(linkName)
        request_proof_requests = request_data.get('proof-requests',
                                                  None)
        nonce = link_request.get(NONCE)
        if request_proof_requests:
            for icr in request_proof_requests:
                # match is found if name and version are same
                matchedProofRequest = next(
                    (cr for cr in link.proofRequests
                     if (cr.name == icr[NAME] and cr.version == icr[VERSION])),
                    None
                )

                # if link.requestedProofs contains any claim request
                if matchedProofRequest:
                    # merge 'attributes' and 'verifiableAttributes'
                    matchedProofRequest.attributes = {
                        **matchedProofRequest.attributes,
                        **icr[ATTRIBUTES]
                    }
                    matchedProofRequest.verifiableAttributes = dict(
                        matchedProofRequest.verifiableAttributes, **icr[VERIFIABLE_ATTRIBUTES])

                else:
                    # otherwise append proof request to link
                    link.proofRequests.append(
                        ProofRequest(
                            icr[NAME],
                            icr[VERSION],
                            getNonceForProof(nonce),
                            attributes=icr[ATTRIBUTES],
                            verifiableAttributes=icr[VERIFIABLE_ATTRIBUTES]))

            return link
        else:
            raise ConnectionAlreadyExists

    def accept_request(self, link: Union[str, Connection]):
        if isinstance(link, str):
            link = self.wallet.getConnection(link, required=True)
        elif isinstance(link, Connection):
            pass
        else:
            raise TypeError(
                "Type of connection must be either string or Link but "
                "provided {}".format(
                    type(link)))
        # TODO should move to wallet in a method like accept(link)
        if not link.localIdentifier:
            self.create_identifier_for_link(link)
        msg = {
            TYPE: ACCEPT_INVITE,
            # TODO should not send this... because origin should be the sender
            NONCE: link.request_nonce,
            VERKEY: self.wallet.getVerkey(link.localIdentifier)
        }
        logger.debug("{} accepting request from {} with id {}".
                     format(self.name, link.name, link.remoteIdentifier))
        self.logger.info('Accepting request with nonce {} from id {}'
                         .format(link.request_nonce, link.remoteIdentifier))
        self.signAndSendToLink(msg, link.name)

    # def _handleSyncNymResp(self, link, additionalCallback):
    #     def _(reply, err):
    #         if err:
    #             raise RuntimeError(err)
    #         reqId = self._updateLinkWithLatestInfo(link, reply)
    #         if reqId:
    #             self.loop.call_later(.2,
    #                                  self.executeWhenResponseRcvd,
    #                                  time.time(), 8000,
    #                                  self.loop, reqId, PONG, True,
    #                                  additionalCallback, reply, err)
    #         else:
    #             additionalCallback(reply, err)
    #
    #     return _

    def create_identifier_for_link(self, link):
        signer = DidSigner()
        self.wallet.addIdentifier(signer=signer)
        link.localIdentifier = signer.identifier
        link.localVerkey = signer.verkey

    def _handleSyncResp(self, link, additionalCallback):
        def _(reply, err):
            if err:
                raise RuntimeError(err)
            reqId = self._updateLinkWithLatestInfo(link, reply)
            if reqId:
                self.loop.call_later(.2,
                                     self.executeWhenResponseRcvd,
                                     time.time(), 8000,
                                     self.loop, reqId, PONG, True,
                                     additionalCallback, reply, err)
            else:
                if callable(additionalCallback):
                    additionalCallback(reply, err)

        return _

    def _updateLinkWithLatestInfo(self, link: Connection, reply):
        if DATA in reply and reply[DATA]:
            data = json.loads(reply[DATA])

            verkey = data.get(VERKEY)
            if verkey is not None:
                link.remoteVerkey = data[VERKEY]

            ep = data.get(ENDPOINT)
            if isinstance(ep, dict):
                # TODO: Validate its an IP port pair or a malicious entity
                # can crash the code
                if 'ha' in ep:
                    ip, port = ep['ha'].split(":")
                    link.remoteEndPoint = (ip, int(port))
                if PUBKEY in ep:
                    link.remotePubkey = ep[PUBKEY]
                else:
                    link.remotePubkey = friendlyVerkeyToPubkey(
                        link.full_remote_verkey) if link.full_remote_verkey else None

            link.connection_last_synced = datetime.now()
            self.notifyMsgListener(
                "    Connection {} synced".format(link.name))

    def _pingToEndpoint(self, name, endpoint):
        self.notifyMsgListener("\nPinging target endpoint: {}".
                               format(endpoint))
        reqId = self.sendPing(linkName=name)
        return reqId

    def sync(self, linkName, doneCallback=None):
        if not self.client.isReady():
            raise NotConnectedToNetwork
        link = self.wallet.getConnection(linkName, required=True)
        identifier = link.remoteIdentifier
        identity = Identity(identifier=identifier)
        req = self.wallet.requestIdentity(identity,
                                          sender=self.wallet.defaultId)

        self.client.submitReqs(req)

        self.loop.call_later(.2,
                             ensureReqCompleted,
                             self.loop,
                             (req.identifier, req.reqId),
                             self.client,
                             self._handleSyncResp(link, None))

        attrib = Attribute(name=ENDPOINT,
                           value=None,
                           dest=identifier,
                           ledgerStore=LedgerStore.RAW)

        req = self.wallet.requestAttribute(
            attrib, sender=self.wallet.defaultId)
        self.client.submitReqs(req)

        self.loop.call_later(.2,
                             ensureReqCompleted,
                             self.loop,
                             (req.identifier, req.reqId),
                             self.client,
                             self._handleSyncResp(link, doneCallback))

    def executeWhenResponseRcvd(self, startTime, maxCheckForMillis,
                                loop, reqId, respType,
                                checkIfLinkExists, clbk, *args):

        if isMaxCheckTimeExpired(startTime, maxCheckForMillis):
            clbk(
                None, "No response received within specified time ({} mills). "
                "Retry the command and see if that works.\n". format(maxCheckForMillis))
        else:
            found = False
            rcvdResponses = self.rcvdMsgStore.get(reqId)
            if rcvdResponses:
                for msg in rcvdResponses:
                    body, frm = msg
                    if body.get(TYPE) == respType:
                        if checkIfLinkExists:
                            identifier = body.get(IDENTIFIER)
                            li = self._getLinkByTarget(
                                getCryptonym(identifier))
                            linkCheckOk = li is not None
                        else:
                            linkCheckOk = True

                        if linkCheckOk:
                            found = True
                            break

            if found:
                clbk(*args)
            else:
                loop.call_later(.2, self.executeWhenResponseRcvd,
                                startTime, maxCheckForMillis, loop,
                                reqId, respType, checkIfLinkExists, clbk, *args)
