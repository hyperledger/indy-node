import json
from typing import Optional

from plenum.common.txn_util import get_seq_no, get_from, get_payload_data, get_type
from plenum.common.types import f

from anoncreds.protocol.exceptions import SchemaNotFoundError
from ledger.util import F
from stp_core.loop.eventually import eventually
from plenum.common.exceptions import NoConsensusYet, OperationError
from stp_core.common.log import getlogger
from plenum.common.constants import TXN_TYPE, DATA, NAME, \
    VERSION, CURRENT_PROTOCOL_VERSION, \
    DOMAIN_LEDGER_ID

from indy_common.constants import GET_SCHEMA, SCHEMA, \
    GET_CLAIM_DEF, CLAIM_DEF, PRIMARY, REVOCATION, GET_TXNS, CLAIM_DEF_SCHEMA_REF, CLAIM_DEF_FROM, \
    CLAIM_DEF_SIGNATURE_TYPE, CLAIM_DEF_TAG, CLAIM_DEF_TAG_DEFAULT, SCHEMA_FROM, SCHEMA_NAME, SCHEMA_VERSION, \
    SCHEMA_ATTR_NAMES, CLAIM_DEF_PUBLIC_KEYS

from anoncreds.protocol.repo.public_repo import PublicRepo
from anoncreds.protocol.types import Schema, ID, PublicKey, \
    RevocationPublicKey, AccumulatorPublicKey, \
    Accumulator, Tails, TimestampType
from indy_common.types import Request
from indy_common.util import get_reply_if_confirmed


def _ensureReqCompleted(reqKey, client, clbk):
    reply, err = get_reply_if_confirmed(client, *reqKey)
    if err:
        raise OperationError(err)

    if reply is None:
        raise NoConsensusYet('not completed')

    return clbk(reply, err)


def _getData(result, error):
    data = result.get(DATA, {})
    # TODO: we have an old txn in the live pool where DATA is stored a json string.
    # We can get rid of the code above once we create a versioning support in
    # txns
    if isinstance(data, str):
        data = json.loads(data)
    seqNo = result.get(F.seqNo.name)
    return data, seqNo


def _submitData(result, error):
    data = get_payload_data(result)
    seqNo = get_seq_no(result)
    return data, seqNo


logger = getlogger()


class IndyPublicRepo(PublicRepo):
    def __init__(self, client, wallet):
        self.client = client
        self.wallet = wallet
        self.displayer = print

    async def getSchema(self, id: ID) -> Optional[Schema]:
        data = None
        issuer_id = None
        if id.schemaKey:
            issuer_id = id.schemaKey.issuerId
            op = {
                SCHEMA_FROM: issuer_id,
                TXN_TYPE: GET_SCHEMA,
                DATA: {
                    SCHEMA_NAME: id.schemaKey.name,
                    SCHEMA_VERSION: id.schemaKey.version,
                }
            }
            data, seqNo = await self._sendGetReq(op)

        else:
            op = {
                f.LEDGER_ID.nm: DOMAIN_LEDGER_ID,
                TXN_TYPE: GET_TXNS,
                DATA: id.schemaId
            }
            res, seqNo = await self._sendGetReq(op)
            if res and get_type(res) == SCHEMA:
                issuer_id = get_from(res)
                data = get_payload_data(res)[DATA]

        if not data or SCHEMA_ATTR_NAMES not in data:
            raise SchemaNotFoundError(
                'No schema with ID={} and key={}'.format(
                    id.schemaId,
                    id.schemaKey))

        return Schema(name=data[NAME],
                      version=data[VERSION],
                      attrNames=data[SCHEMA_ATTR_NAMES],
                      issuerId=issuer_id,
                      seqId=seqNo)

    async def getPublicKey(self, id: ID = None, signatureType='CL') -> Optional[PublicKey]:
        op = {
            TXN_TYPE: GET_CLAIM_DEF,
            CLAIM_DEF_SCHEMA_REF: id.schemaId,
            CLAIM_DEF_FROM: id.schemaKey.issuerId,
            CLAIM_DEF_SIGNATURE_TYPE: signatureType,
            CLAIM_DEF_TAG: CLAIM_DEF_TAG_DEFAULT
        }

        data, seqNo = await self._sendGetReq(op)
        if not data:
            raise ValueError(
                'No CLAIM_DEF for schema with ID={} and key={}'.format(
                    id.schemaId, id.schemaKey))
        data = data[PRIMARY]
        pk = PublicKey.from_str_dict(data)._replace(seqId=seqNo)
        return pk

    async def getPublicKeyRevocation(self, id: ID,
                                     signatureType='CL') -> Optional[RevocationPublicKey]:
        op = {
            TXN_TYPE: GET_CLAIM_DEF,
            CLAIM_DEF_SCHEMA_REF: id.schemaId,
            CLAIM_DEF_FROM: id.schemaKey.issuerId,
            CLAIM_DEF_SIGNATURE_TYPE: signatureType,
            CLAIM_DEF_TAG: CLAIM_DEF_TAG_DEFAULT
        }
        data, seqNo = await self._sendGetReq(op)
        if not data:
            raise ValueError(
                'No CLAIM_DEF for schema with ID={} and key={}'.format(
                    id.schemaId, id.schemaKey))
        if REVOCATION not in data:
            return None
        data = data[REVOCATION]
        pkR = RevocationPublicKey.fromStrDict(data)._replace(seqId=seqNo)
        return pkR

    async def getPublicKeyAccumulator(self, id: ID) -> AccumulatorPublicKey:
        raise NotImplementedError

    async def getAccumulator(self, id: ID) -> Accumulator:
        raise NotImplementedError

    async def getTails(self, id: ID) -> Tails:
        raise NotImplementedError

    # SUBMIT

    async def submitSchema(self,
                           schema: Schema) -> Schema:
        data = {
            SCHEMA_NAME: schema.name,
            SCHEMA_VERSION: schema.version,
            SCHEMA_ATTR_NAMES: schema.attrNames
        }
        op = {
            TXN_TYPE: SCHEMA,
            DATA: data
        }
        _, seqNo = await self._sendSubmitReq(op)
        if seqNo:
            schema = schema._replace(issuerId=self.wallet.defaultId,
                                     seqId=seqNo)
            return schema

    async def submitPublicKeys(self,
                               id: ID,
                               pk: PublicKey,
                               pkR: RevocationPublicKey = None,
                               signatureType='CL') -> \
            (PublicKey, RevocationPublicKey):

        data = {}
        if pk is not None:
            data[PRIMARY] = pk.to_str_dict()
        if pkR is not None:
            data[REVOCATION] = pkR.toStrDict()

        op = {
            TXN_TYPE: CLAIM_DEF,
            CLAIM_DEF_SCHEMA_REF: id.schemaId,
            CLAIM_DEF_PUBLIC_KEYS: data,
            CLAIM_DEF_SIGNATURE_TYPE: signatureType,
            CLAIM_DEF_TAG: CLAIM_DEF_TAG_DEFAULT
        }

        _, seqNo = await self._sendSubmitReq(op)

        if seqNo:
            pk = pk._replace(seqId=seqNo)

            if pkR is not None:
                pkR = pkR._replace(seqId=seqNo)

            return pk, pkR

    async def submitAccumulator(self, id: ID, accumPK: AccumulatorPublicKey,
                                accum: Accumulator, tails: Tails):
        raise NotImplementedError

    async def submitAccumUpdate(self, id: ID, accum: Accumulator,
                                timestampMs: TimestampType):
        raise NotImplementedError

    async def _sendSubmitReq(self, op):
        return await self._sendReq(op, _submitData)

    async def _sendGetReq(self, op):
        return await self._sendReq(op, _getData)

    async def _sendReq(self, op, clbk):
        req = Request(identifier=self.wallet.defaultId,
                      operation=op,
                      protocolVersion=CURRENT_PROTOCOL_VERSION)
        req = self.wallet.prepReq(req)
        self.client.submitReqs(req)
        try:
            # TODO: Come up with an explanation, why retryWait had to be
            # increases to 1 from .5 to pass some tests and from 1 to 2 to
            # pass some other tests. The client was not getting a chance to
            # service its stack, we need to find a way to stop this starvation.
            resp = await eventually(_ensureReqCompleted,
                                    (req.identifier, req.reqId),
                                    self.client, clbk,
                                    timeout=20, retryWait=2)
        except NoConsensusYet:
            raise TimeoutError('Request timed out')
        return resp
