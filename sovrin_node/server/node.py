import json
from hashlib import sha256
from copy import deepcopy
from operator import itemgetter
from typing import Iterable, Any

import pyorient
from ledger.compact_merkle_tree import CompactMerkleTree
from ledger.ledger import Ledger
from ledger.serializers.compact_serializer import CompactSerializer
from ledger.util import F
from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest
from plenum.common.log import getlogger
from plenum.common.txn import RAW, ENC, HASH, NAME, VERSION, ORIGIN
from plenum.common.types import Reply, RequestAck, RequestNack, f, \
    NODE_PRIMARY_STORAGE_SUFFIX, OPERATION
from plenum.common.util import error
from plenum.persistence.storage import initStorage
from plenum.server.node import Node as PlenumNode

from sovrin_common.config_util import getConfig
from sovrin_common.txn import TXN_TYPE, \
    TARGET_NYM, allOpKeys, validTxnTypes, ATTRIB, SPONSOR, NYM,\
    ROLE, STEWARD, USER, GET_ATTR, DISCLO, DATA, GET_NYM, \
    TXN_ID, TXN_TIME, reqOpKeys, GET_TXNS, LAST_TXN, TXNS, \
    getTxnOrderedFields, CLAIM_DEF, GET_CLAIM_DEF, isValidRole, openTxns, \
    ISSUER_KEY, GET_ISSUER_KEY, REF
from sovrin_common.types import Request
from sovrin_common.util import dateTimeEncoding
from sovrin_common.persistence import identity_graph
from sovrin_node.persistence.secondary_storage import SecondaryStorage
from sovrin_node.server.client_authn import TxnBasedAuthNr

logger = getlogger()


class Node(PlenumNode):
    keygenScript = "init_sovrin_raet_keep"

    authorizedAdders = {
        STEWARD: (STEWARD,),
        SPONSOR: (STEWARD,),
        USER: (STEWARD, SPONSOR),
    }

    def __init__(self,
                 name,
                 nodeRegistry=None,
                 clientAuthNr=None,
                 ha=None,
                 cliname=None,
                 cliha=None,
                 basedirpath=None,
                 primaryDecider=None,
                 pluginPaths: Iterable[str] = None,
                 storage=None,
                 config=None):
        self.config = config or getConfig()
        self.graphStore = self.getGraphStorage(name)
        super().__init__(name=name,
                         nodeRegistry=nodeRegistry,
                         clientAuthNr=clientAuthNr,
                         ha=ha,
                         cliname=cliname,
                         cliha=cliha,
                         basedirpath=basedirpath,
                         primaryDecider=primaryDecider,
                         pluginPaths=pluginPaths,
                         storage=storage,
                         config=self.config)
        self._addTxnsToGraphIfNeeded()

    def getSecondaryStorage(self):
        return SecondaryStorage(self.graphStore, self.primaryStorage)

    def getGraphStorage(self, name):
        return identity_graph.IdentityGraph(self._getOrientDbStore(name,
                                                    pyorient.DB_TYPE_GRAPH))

    def getPrimaryStorage(self):
        """
        This is usually an implementation of Ledger
        """
        if self.config.primaryStorage is None:
            fields = getTxnOrderedFields()
            return Ledger(CompactMerkleTree(hashStore=self.hashStore),
                          dataDir=self.dataLocation,
                          serializer=CompactSerializer(fields=fields),
                          fileName=self.config.domainTransactionsFile,
                          ensureDurability=self.config.EnsureLedgerDurability)
        else:
            return initStorage(self.config.primaryStorage,
                               name=self.name + NODE_PRIMARY_STORAGE_SUFFIX,
                               dataDir=self.dataLocation,
                               config=self.config)

    def _addTxnsToGraphIfNeeded(self):
        i = 0
        txnCountInGraph = self.graphStore.countTxns()
        for seqNo, txn in self.domainLedger.getAllTxn().items():
            if seqNo > txnCountInGraph:
                txn[F.seqNo.name] = seqNo
                self.storeTxnInGraph(txn)
                i += 1
        logger.debug("{} adding {} transactions to graph from ledger".
                     format(self, i))
        return i

    def isSignatureVerificationNeeded(self, msg: Any):
        op = msg.get(OPERATION)
        if op:
            if op.get(TXN_TYPE) in openTxns:
                return False
        return True

    def checkValidOperation(self, identifier, reqId, msg):
        self.checkValidSovrinOperation(identifier, reqId, msg)
        super().checkValidOperation(identifier, reqId, msg)

    def checkValidSovrinOperation(self, identifier, reqId, msg):
        unknownKeys = set(msg.keys()).difference(set(allOpKeys))
        if unknownKeys:
            raise InvalidClientRequest(identifier, reqId,
                                       'invalid keys "{}"'.
                                       format(",".join(unknownKeys)))

        missingKeys = set(reqOpKeys).difference(set(msg.keys()))
        if missingKeys:
            raise InvalidClientRequest(identifier, reqId,
                                       'missing required keys "{}"'.
                                       format(",".join(missingKeys)))

        if msg[TXN_TYPE] not in validTxnTypes:
            raise InvalidClientRequest(identifier, reqId, 'invalid {}: {}'.
                                       format(TXN_TYPE, msg[TXN_TYPE]))

        if msg[TXN_TYPE] == ATTRIB:
            dataKeys = {RAW, ENC, HASH}.intersection(set(msg.keys()))
            if len(dataKeys) != 1:
                raise InvalidClientRequest(identifier, reqId,
                                           '{} should have one and only one of '
                                           '{}, {}, {}'
                                           .format(ATTRIB, RAW, ENC, HASH))
            if RAW in dataKeys:
                try:
                    json.loads(msg[RAW])
                except:
                    raise InvalidClientRequest(identifier, reqId,
                                               'raw attribute {} should be '
                                               'JSON'.format(msg[RAW]))

            if not (not msg.get(TARGET_NYM) or
                    self.graphStore.hasNym(msg[TARGET_NYM])):
                raise InvalidClientRequest(identifier, reqId,
                                           '{} should be added before adding '
                                           'attribute for it'.
                                           format(TARGET_NYM))

        if msg[TXN_TYPE] == NYM:
            role = msg.get(ROLE) or USER
            nym = msg.get(TARGET_NYM)
            if not nym:
                raise InvalidClientRequest(identifier, reqId,
                                           "{} needs to be present".
                                           format(TARGET_NYM))
            if not isValidRole(role):
                raise InvalidClientRequest(identifier, reqId,
                                           "{} not a valid role".
                                           format(role))
            # Only
            if not self.canNymRequestBeProcessed(identifier, msg):
                raise InvalidClientRequest(identifier, reqId,
                                           "{} is already present".
                                           format(nym))

    def checkRequestAuthorized(self, request: Request):
        op = request.operation
        typ = op[TXN_TYPE]

        s = self.graphStore  # type: identity_graph.IdentityGraph

        origin = request.identifier

        if typ == NYM:
            try:
                originRole = s.getRole(origin)
            except Exception as ex:
                raise UnauthorizedClientRequest(
                    request.identifier,
                    request.reqId,
                    "Nym {} not added to the ledger yet".format(origin))
            role = op.get(ROLE) or USER
            authorizedAdder = self.authorizedAdders[role]
            if originRole not in authorizedAdder:
                raise UnauthorizedClientRequest(
                    request.identifier,
                    request.reqId,
                    "{} cannot add {}".format(originRole, role))
        elif typ == ATTRIB:
            if op.get(TARGET_NYM) and \
                op[TARGET_NYM] != request.identifier and \
                    not s.getSponsorFor(op[TARGET_NYM]) == origin:

                raise UnauthorizedClientRequest(
                        request.identifier,
                        request.reqId,
                        "Only user's sponsor can add attribute for that user")
        # TODO: Just for now. Later do something meaningful here
        elif typ in [DISCLO, GET_ATTR, CLAIM_DEF, GET_CLAIM_DEF, ISSUER_KEY,
                     GET_ISSUER_KEY]:
            pass
        else:
            return super().checkRequestAuthorized(request)

    def canNymRequestBeProcessed(self, identifier, msg):
        nym = msg.get(TARGET_NYM)
        if self.graphStore.hasNym(nym) and \
                self.graphStore.getSponsorFor(nym) != identifier:
            return False
        return True

    def defaultAuthNr(self):
        return TxnBasedAuthNr(self.graphStore)

    def processGetNymReq(self, request: Request, frm: str):
        self.transmitToClient(RequestAck(*request.key), frm)
        nym = request.operation[TARGET_NYM]
        txn = self.graphStore.getAddNymTxn(nym)
        txnId = self.genTxnId(request.identifier, request.reqId)
        # TODO: We should have a single JSON encoder which does the
        # encoding for us, like sorting by keys, handling datetime objects.
        result = {f.IDENTIFIER.nm: request.identifier,
                  f.REQ_ID.nm: request.reqId,
                  DATA: json.dumps(txn, sort_keys=True) if txn else None,
                  TXN_ID: txnId
                  }
        result.update(request.operation)
        self.transmitToClient(Reply(result), frm)

    def processGetTxnReq(self, request: Request, frm: str):
        nym = request.operation[TARGET_NYM]
        origin = request.identifier
        if nym != origin:
            # TODO not sure this is correct; why does it matter?
            msg = "You can only receive transactions for yourself"
            self.transmitToClient(RequestNack(*request.key, msg), frm)
        else:
            self.transmitToClient(RequestAck(*request.key), frm)
            data = request.operation.get(DATA)
            addNymTxn = self.graphStore.getAddNymTxn(origin)
            txnIds = [addNymTxn[TXN_ID], ] + self.graphStore. \
                getAddAttributeTxnIds(origin)
            # If sending transactions to a user then should send user's
            # sponsor creation transaction also
            if addNymTxn.get(ROLE) == USER:
                sponsorNymTxn = self.graphStore.getAddNymTxn(
                    addNymTxn.get(f.IDENTIFIER.nm))
                txnIds = [sponsorNymTxn[TXN_ID], ] + txnIds
            # TODO: Remove this log statement
            logger.debug("{} getting replies for {}".format(self, txnIds))
            result = self.secondaryStorage.getReplies(*txnIds, seqNo=data)
            txns = sorted(list(result.values()), key=itemgetter(F.seqNo.name))
            lastTxn = str(txns[-1][F.seqNo.name]) if len(txns) > 0 else data
            result = {
                TXN_ID: self.genTxnId(
                    request.identifier, request.reqId)
            }
            result.update(request.operation)
            # TODO: We should have a single JSON encoder which does the
            # encoding for us, like sorting by keys, handling datetime objects.
            result[DATA] = json.dumps({
                LAST_TXN: lastTxn,
                TXNS: txns
            }, default=dateTimeEncoding, sort_keys=True)
            result.update({
                f.IDENTIFIER.nm: request.identifier,
                f.REQ_ID.nm: request.reqId,
            })
            self.transmitToClient(Reply(result), frm)

    def processGetClaimDefReq(self, request: Request, frm: str):
        issuerNym = request.operation[TARGET_NYM]
        name = request.operation[DATA][NAME]
        version = request.operation[DATA][VERSION]
        claimDef = self.graphStore.getClaimDef(issuerNym, name, version)
        result = {
            TXN_ID: self.genTxnId(
                request.identifier, request.reqId)
        }
        result.update(request.operation)
        result[DATA] = json.dumps(claimDef, sort_keys=True)
        result.update({
            f.IDENTIFIER.nm: request.identifier,
            f.REQ_ID.nm: request.reqId,
        })
        self.transmitToClient(Reply(result), frm)

    def processGetAttrsReq(self, request: Request, frm: str):
        self.transmitToClient(RequestAck(*request.key), frm)
        attrName = request.operation[RAW]
        nym = request.operation[TARGET_NYM]
        attrWithSeqNo = self.graphStore.getRawAttrs(nym, attrName)
        result = {
            TXN_ID: self.genTxnId(
                request.identifier, request.reqId)
        }
        if attrWithSeqNo:
            attr = {attrName: attrWithSeqNo[attrName][0]}
            result[DATA] = json.dumps(attr, sort_keys=True)
            result[F.seqNo.name] = attrWithSeqNo[attrName][1]
        result.update(request.operation)
        result.update({
            f.IDENTIFIER.nm: request.identifier,
            f.REQ_ID.nm: request.reqId,
        })
        self.transmitToClient(Reply(result), frm)

    def processGetIssuerKeyReq(self, request: Request, frm: str):
        self.transmitToClient(RequestAck(*request.key), frm)
        keys = self.graphStore.getIssuerKeys(request.operation[ORIGIN],
                                             request.operation[REF])
        result = {
            TXN_ID: self.genTxnId(
                request.identifier, request.reqId)
        }
        result.update(request.operation)
        result[DATA] = json.dumps(keys, sort_keys=True)
        result.update({
            f.IDENTIFIER.nm: request.identifier,
            f.REQ_ID.nm: request.reqId,
        })
        self.transmitToClient(Reply(result), frm)

    def processRequest(self, request: Request, frm: str):
        if request.operation[TXN_TYPE] == GET_NYM:
            self.processGetNymReq(request, frm)
        elif request.operation[TXN_TYPE] == GET_TXNS:
            self.processGetTxnReq(request, frm)
        elif request.operation[TXN_TYPE] == GET_CLAIM_DEF:
            self.processGetClaimDefReq(request, frm)
        elif request.operation[TXN_TYPE] == GET_ATTR:
            self.processGetAttrsReq(request, frm)
        elif request.operation[TXN_TYPE] == GET_ISSUER_KEY:
            self.processGetIssuerKeyReq(request, frm)
        else:
            super().processRequest(request, frm)

    def storeTxnAndSendToClient(self, reply):
        """
        Does 4 things in following order
         1. Add reply to ledger.
         2. Send the reply to client.
         3. Add the reply to identity graph if needed.
         4. Add the reply to storage so it can be served later if the
         client requests it.
        """
        result = reply.result
        txnWithMerkleInfo = self.storeTxnInLedger(result)
        self.sendReplyToClient(Reply(txnWithMerkleInfo),
                               (result[f.IDENTIFIER.nm], result[f.REQ_ID.nm]))
        reply.result[F.seqNo.name] = txnWithMerkleInfo.get(F.seqNo.name)
        self.storeTxnInGraph(reply.result)

    def storeTxnInLedger(self, result):
        if result[TXN_TYPE] == ATTRIB:
            result = self.hashAttribTxn(result)
        merkleInfo = self.addToLedger(result)
        result.update(merkleInfo)
        return result

    @staticmethod
    def hashAttribTxn(result):
        # Creating copy of result so that `RAW`, `ENC` or `HASH` can be
        # replaced by their hashes. We do not insert actual attribute data
        # in the ledger but only the hash of it.
        result = deepcopy(result)
        if RAW in result:
            result[RAW] = sha256(result[RAW].encode()).hexdigest()
        elif ENC in result:
            result[ENC] = sha256(result[ENC].encode()).hexdigest()
        elif HASH in result:
            result[HASH] = result[HASH]
        else:
            error("Transaction missing required field")
        return result

    def storeTxnInGraph(self, result):
        result = deepcopy(result)
        # Remove root hash and audit path from result if present since they can
        # be generated on the fly from the ledger so no need to store it
        result.pop(F.rootHash.name, None)
        result.pop(F.auditPath.name, None)

        if result[TXN_TYPE] == NYM:
            self.graphStore.addNymTxnToGraph(result)
        elif result[TXN_TYPE] == ATTRIB:
            self.graphStore.addAttribTxnToGraph(result)
        elif result[TXN_TYPE] == CLAIM_DEF:
            self.graphStore.addClaimDefTxnToGraph(result)
        elif result[TXN_TYPE] == ISSUER_KEY:
            self.graphStore.addIssuerKeyTxnToGraph(result)
        else:
            logger.debug("Got an unknown type {} to process".
                         format(result[TXN_TYPE]))

    # # TODO: Need to fix the signature
    # def sendReplyToClient(self, reply):
    #     identifier = reply.result.get(f.IDENTIFIER.nm)
    #     reqId = reply.result.get(f.REQ_ID.nm)
    #     # In case of genesis transactions when no identifier is present
    #     key = (identifier, reqId)
    #     if (identifier, reqId) in self.requestSender:
    #         self.transmitToClient(reply, self.requestSender.pop(key))
    #     else:
    #         logger.debug("Could not find key {} to send reply".
    #                      format(key))

    def addToLedger(self, txn):
        merkleInfo = self.primaryStorage.append(txn)
        return merkleInfo

    def getReplyFor(self, request):
        result = self.secondaryStorage.getReply(request.identifier,
                                                request.reqId,
                                                type=request.operation[TXN_TYPE])
        if result:
            if request.operation[TXN_TYPE] == ATTRIB:
                result = self.hashAttribTxn(result)
            return Reply(result)
        else:
            return None

    def doCustomAction(self, ppTime: float, req: Request) -> None:
        """
        Execute the REQUEST sent to this Node

        :param ppTime: the time at which PRE-PREPARE was sent
        :param req: the client REQUEST
        """
        if req.operation[TXN_TYPE] == NYM and not \
                self.canNymRequestBeProcessed(req.identifier, req.operation):
            reason = "nym {} is already added".format(req.operation[TARGET_NYM])
            if req.key in self.requestSender:
                self.transmitToClient(RequestNack(*req.key, reason),
                                      self.requestSender.pop(req.key))
        else:
            reply = self.generateReply(int(ppTime), req)
            self.storeTxnAndSendToClient(reply)

    def generateReply(self, ppTime: float, req: Request):
        operation = req.operation
        txnId = self.genTxnId(req.identifier, req.reqId)
        result = {TXN_ID: txnId, TXN_TIME: int(ppTime)}
        result.update(operation)
        result.update({
            f.IDENTIFIER.nm: req.identifier,
            f.REQ_ID.nm: req.reqId,
        })

        return Reply(result)
