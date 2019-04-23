import json
from binascii import hexlify
from copy import deepcopy
from json import JSONDecodeError
from typing import List, Callable

import base58
from indy_common.serialization import attrib_raw_data_serializer

from common.exceptions import LogicError
from indy_common.auth import Authoriser
from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_map import auth_map, anyone_can_write_map
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.config_util import getConfig
from indy_common.constants import NYM, ROLE, ATTRIB, SCHEMA, CLAIM_DEF, \
    GET_NYM, GET_ATTR, GET_SCHEMA, GET_CLAIM_DEF, REVOC_REG_DEF, REVOC_REG_ENTRY, ISSUANCE_TYPE, \
    REVOC_REG_DEF_ID, VALUE, ISSUANCE_BY_DEFAULT, ISSUANCE_ON_DEMAND, TAG, CRED_DEF_ID, \
    GET_REVOC_REG_DEF, ID, GET_REVOC_REG, GET_REVOC_REG_DELTA, REVOC_TYPE, \
    TIMESTAMP, FROM, TO, ISSUED, REVOKED, STATE_PROOF_FROM, ACCUM_FROM, ACCUM_TO, \
    CLAIM_DEF_SIGNATURE_TYPE, SCHEMA_NAME, SCHEMA_VERSION, REF
from indy_common.req_utils import get_read_schema_name, get_read_schema_version, \
    get_read_schema_from, get_write_schema_name, get_write_schema_version, get_read_claim_def_from, \
    get_read_claim_def_signature_type, get_read_claim_def_schema_ref, get_read_claim_def_tag
from indy_common.state import domain
from indy_common.state.domain import make_state_path_for_revoc_def
from indy_common.types import Request
from plenum.common.constants import TXN_TYPE, TARGET_NYM, RAW, ENC, HASH, \
    VERKEY, \
    TXN_TIME
from plenum.common.exceptions import InvalidClientRequest, \
    UnauthorizedClientRequest, UnknownIdentifier
from plenum.common.txn_util import get_type, get_payload_data, get_from, get_seq_no, get_txn_time, get_req_id
from plenum.common.types import f
from plenum.common.constants import TRUSTEE
from plenum.server.domain_req_handler import DomainRequestHandler as PHandler
from stp_core.common.log import getlogger
from indy_node.server.revocation_strategy import RevokedStrategy, IssuedStrategy

logger = getlogger()


class StateValue:
    def __init__(self, root_hash=None, value=None, seq_no=None, update_time=None, proof=None):
        self.root_hash = root_hash
        self.value = value
        self.seq_no = seq_no
        self.update_time = update_time
        self.proof = proof


class DomainReqHandler(PHandler):
    write_types = {NYM, ATTRIB, SCHEMA, CLAIM_DEF, REVOC_REG_DEF, REVOC_REG_ENTRY}
    query_types = {GET_NYM, GET_ATTR, GET_SCHEMA, GET_CLAIM_DEF,
                   GET_REVOC_REG_DEF, GET_REVOC_REG, GET_REVOC_REG_DELTA}
    revocation_strategy_map = {
        ISSUANCE_BY_DEFAULT: RevokedStrategy,
        ISSUANCE_ON_DEMAND: IssuedStrategy,
    }

    def __init__(self, ledger, state, config, requestProcessor,
                 idrCache, attributeStore, bls_store, write_req_validator, ts_store=None):
        super().__init__(ledger, state, config, requestProcessor, bls_store, ts_store=ts_store)
        self.idrCache = idrCache
        self.attributeStore = attributeStore

        self.static_validation_handlers = {}
        self.dynamic_validation_handlers = {}
        self.state_update_handlers = {}
        self.query_handlers = {}
        self.post_batch_creation_handlers = []
        self.post_batch_commit_handlers = []
        self.post_batch_rejection_handlers = []
        self.write_req_validator = write_req_validator

        self._add_default_handlers()

    def _updateStateWithSingleTxn(self, txn, isCommitted=False):
        txn_type = get_type(txn)
        if txn_type in self.state_update_handlers:
            self.state_update_handlers[txn_type](txn, isCommitted)
        else:
            logger.debug(
                'Cannot apply request of type {} to state'.format(txn_type))

    def gen_txn_path(self, txn):

        """Return path to state as 'str' type or None"""
        txn_type = get_type(txn)
        if txn_type not in self.state_update_handlers:
            logger.error('Cannot generate id for txn of type {}'.format(txn_type))
            return None

        if txn_type == NYM:
            nym = get_payload_data(txn).get(TARGET_NYM)
            binary_digest = domain.make_state_path_for_nym(nym)
            return hexlify(binary_digest).decode()
        elif txn_type == ATTRIB:
            path = domain.prepare_attr_for_state(txn, path_only=True)
            return path.decode()
        elif txn_type == SCHEMA:
            path = domain.prepare_schema_for_state(txn, path_only=True)
            return path.decode()
        elif txn_type == CLAIM_DEF:
            path = domain.prepare_claim_def_for_state(txn, path_only=True)
            return path.decode()
        elif txn_type == REVOC_REG_DEF:
            path = domain.prepare_revoc_def_for_state(txn, path_only=True)
            return path.decode()
        elif txn_type == REVOC_REG_ENTRY:
            path = domain.prepare_revoc_reg_entry_for_state(txn, path_only=True)
            return path.decode()

        raise NotImplementedError("path construction is not implemented for type {}".format(txn_type))

    def commit(self, txnCount, stateRoot, txnRoot, ppTime) -> List:
        r = super().commit(txnCount, stateRoot, txnRoot, ppTime)
        self.onBatchCommitted(stateRoot)

        return r

    def update_idr_cache(self, stateRoot):
        stateRoot = base58.b58decode(stateRoot.encode())
        self.idrCache.onBatchCommitted(stateRoot)

    def doStaticValidation(self, request: Request):
        identifier, req_id, operation = request.identifier, request.reqId, request.operation
        txn_type = operation[TXN_TYPE]
        if txn_type in self.static_validation_handlers:
            self.static_validation_handlers[txn_type](identifier, req_id, operation)

    def _doStaticValidationNym(self, identifier, reqId, operation):
        role = operation.get(ROLE)
        nym = operation.get(TARGET_NYM)
        if not nym:
            raise InvalidClientRequest(identifier, reqId,
                                       "{} needs to be present".
                                       format(TARGET_NYM))
        if not Authoriser.isValidRole(role):
            raise InvalidClientRequest(identifier, reqId,
                                       "{} not a valid role".
                                       format(role))

    def _doStaticValidationAttrib(self, identifier, reqId, operation):
        if not self._validate_attrib_keys(operation):
            raise InvalidClientRequest(identifier, reqId,
                                       '{} should have one and only one of '
                                       '{}, {}, {}'
                                       .format(ATTRIB, RAW, ENC, HASH))

    def _doStaticValidationGetRevocRegDelta(self, identifier, reqId, operation):
        req_ts_to = operation.get(TO, None)
        assert req_ts_to
        req_ts_from = operation.get(FROM, None)

        if req_ts_from and req_ts_from > req_ts_to:
            raise InvalidClientRequest(identifier,
                                       reqId,
                                       "Timestamp FROM more then TO: {} > {}".format(req_ts_from, req_ts_to))

    def validate(self, req: Request, config=None):
        op = req.operation
        txn_type = op[TXN_TYPE]
        if txn_type in self.dynamic_validation_handlers:
            self.dynamic_validation_handlers[txn_type](req)

    @staticmethod
    def _validate_attrib_keys(operation):
        dataKeys = {RAW, ENC, HASH}.intersection(set(operation.keys()))
        return len(dataKeys) == 1

    def _validateNym(self, req: Request):
        op = req.operation

        nymData = self.idrCache.getNym(op[TARGET_NYM], isCommitted=False)
        if not nymData:
            # If nym does not exist
            self._validateNewNym(req, op)
        else:
            self._validateExistingNym(req, op, nymData)

    def _validateNewNym(self, req: Request, op):
        role = op.get(ROLE)
        self.write_req_validator.validate(req,
                                          [AuthActionAdd(txn_type=NYM,
                                                         field=ROLE,
                                                         value=role)])

    def _validateExistingNym(self, req: Request, op, nymData):
        origin = req.identifier
        owner = self.idrCache.getOwnerFor(op[TARGET_NYM], isCommitted=False)
        is_owner = origin == owner

        updateKeys = [ROLE, VERKEY]
        for key in updateKeys:
            if key in op:
                newVal = op[key]
                oldVal = nymData.get(key)
                self.write_req_validator.validate(req,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=key,
                                                                  old_value=oldVal,
                                                                  new_value=newVal,
                                                                  is_owner=is_owner)])

    def _validateAttrib(self, req: Request):
        origin = req.identifier
        op = req.operation

        if not (not op.get(TARGET_NYM) or
                self.hasNym(op[TARGET_NYM], isCommitted=False)):
            raise InvalidClientRequest(origin, req.reqId,
                                       '{} should be added before adding '
                                       'attribute for it'.
                                       format(TARGET_NYM))

        is_owner = self.idrCache.getOwnerFor(op[TARGET_NYM],
                                             isCommitted=False) == origin
        field = None
        value = None
        for key in (RAW, ENC, HASH):
            if key in op:
                field = key
                value = op[key]
                break
        if field is None or value is None:
            raise LogicError('Attribute data cannot be empty')

        get_key = None
        if field == RAW:
            try:
                get_key = attrib_raw_data_serializer.deserialize(value)
                if len(get_key) == 0:
                    raise InvalidClientRequest(origin, req.reqId,
                                               '"row" attribute field must contain non-empty dict'.
                                               format(TARGET_NYM))
                get_key = next(iter(get_key.keys()))
            except JSONDecodeError:
                raise InvalidClientRequest(origin, req.reqId,
                                           'Attribute field must be dict while adding it as a row field'.
                                           format(TARGET_NYM))
        else:
            get_key = value

        if get_key is None:
            raise LogicError('Attribute data must be parsed')

        old_value, seq_no, _, _ = self.getAttr(op[TARGET_NYM], get_key, field, isCommitted=False)

        if seq_no is not None:
            self.write_req_validator.validate(req,
                                              [AuthActionEdit(txn_type=ATTRIB,
                                                              field=field,
                                                              old_value=old_value,
                                                              new_value=value,
                                                              is_owner=is_owner)])
        else:
            self.write_req_validator.validate(req,
                                              [AuthActionAdd(txn_type=ATTRIB,
                                                             field=field,
                                                             value=value,
                                                             is_owner=is_owner)])

    def _validate_schema(self, req: Request):
        # we can not add a Schema with already existent NAME and VERSION
        # sine a Schema needs to be identified by seqNo
        identifier = req.identifier
        schema_name = get_write_schema_name(req)
        schema_version = get_write_schema_version(req)
        schema, _, _, _ = self.getSchema(
            author=identifier,
            schemaName=schema_name,
            schemaVersion=schema_version,
            with_proof=False
        )
        if schema:
            raise InvalidClientRequest(identifier, req.reqId,
                                       '{} can have one and only one SCHEMA with '
                                       'name {} and version {}'
                                       .format(identifier, schema_name, schema_version))
        self.write_req_validator.validate(req,
                                          [AuthActionAdd(txn_type=SCHEMA,
                                                         field='*',
                                                         value='*')])

    def _validate_claim_def(self, req: Request):
        # we can not add a Claim Def with existent ISSUER_DID
        # sine a Claim Def needs to be identified by seqNo
        ref = req.operation[REF]
        try:
            txn = self.ledger.get_by_seq_no_uncommitted(ref)
        except KeyError:
            raise InvalidClientRequest(req.identifier,
                                       req.reqId,
                                       "Mentioned seqNo ({}) doesn't exist.".format(ref))
        if txn['txn']['type'] != SCHEMA:
            raise InvalidClientRequest(req.identifier,
                                       req.reqId,
                                       "Mentioned seqNo ({}) isn't seqNo of the schema.".format(ref))
        # only owner can update claim_def,
        # because his identifier is the primary key of claim_def
        self.write_req_validator.validate(req,
                                          [AuthActionAdd(txn_type=CLAIM_DEF,
                                                         field='*',
                                                         value='*')])

    def _validate_revoc_reg_def(self, req: Request):
        operation = req.operation
        cred_def_id = operation.get(CRED_DEF_ID)
        revoc_def_type = operation.get(REVOC_TYPE)
        revoc_def_tag = operation.get(TAG)
        assert cred_def_id
        assert revoc_def_tag
        assert revoc_def_type
        tags = cred_def_id.split(":")

        revoc_def = make_state_path_for_revoc_def(req.identifier, cred_def_id, revoc_def_type, revoc_def_tag)
        revoc_def_id, _, _, _ = self.lookup(revoc_def, isCommitted=False)

        if revoc_def is None:
            self.write_req_validator.validate(req,
                                              [AuthActionAdd(txn_type=REVOC_REG_DEF,
                                                             field='*',
                                                             value='*')])
        else:
            self.write_req_validator.validate(req,
                                              [AuthActionEdit(txn_type=REVOC_REG_DEF,
                                                              field='*',
                                                              old_value='*',
                                                              new_value='*')])

        cred_def, _, _, _ = self.lookup(cred_def_id, isCommitted=False, with_proof=False)

        if len(tags) != 4 and len(tags) != 5:
            raise InvalidClientRequest(req.identifier,
                                       req.reqId,
                                       "Format of {} field is not acceptable. "
                                       "Expected: 'did:marker:signature_type:schema_ref' or "
                                       "'did:marker:signature_type:schema_ref:tag'".format(CRED_DEF_ID))
        if cred_def is None:
            raise InvalidClientRequest(req.identifier,
                                       req.reqId,
                                       "There is no any CRED_DEF by path: {}".format(cred_def_id))

    def _get_current_revoc_entry_and_revoc_def(self, author_did, revoc_reg_def_id, req_id):
        assert revoc_reg_def_id
        current_entry, _, _, _ = self.getRevocDefEntry(revoc_reg_def_id=revoc_reg_def_id,
                                                       isCommitted=False)
        revoc_def, _, _, _ = self.lookup(revoc_reg_def_id, isCommitted=False, with_proof=False)
        if revoc_def is None:
            raise InvalidClientRequest(author_did,
                                       req_id,
                                       "There is no any REVOC_REG_DEF by path: {}".format(revoc_reg_def_id))
        return current_entry, revoc_def

    def _validate_revoc_reg_entry(self, req: Request):
        author_did = req.identifier
        rev_reg_tags = req.operation[REVOC_REG_DEF_ID]
        current_entry, revoc_def = self._get_current_revoc_entry_and_revoc_def(
            author_did=author_did,
            revoc_reg_def_id=req.operation[REVOC_REG_DEF_ID],
            req_id=req.reqId
        )

        rev_ref_def_author_did = rev_reg_tags.split(":", 1)[0]
        is_owner = rev_ref_def_author_did == author_did

        if current_entry:
            self.write_req_validator.validate(req,
                                              [AuthActionEdit(txn_type=REVOC_REG_ENTRY,
                                                              field='*',
                                                              old_value='*',
                                                              new_value='*',
                                                              is_owner=is_owner)])
        else:
            self.write_req_validator.validate(req,
                                              [AuthActionAdd(txn_type=REVOC_REG_ENTRY,
                                                             field='*',
                                                             value='*',
                                                             is_owner=is_owner)])

        validator_cls = self.get_revocation_strategy(revoc_def[VALUE][ISSUANCE_TYPE])
        validator = validator_cls(self.state)
        validator.validate(current_entry, req)

    def updateNym(self, nym, txn, isCommitted=True):
        updatedData = super().updateNym(nym, txn, isCommitted=isCommitted)
        txn_time = get_txn_time(txn)
        self.idrCache.set(nym,
                          seqNo=get_seq_no(txn),
                          txnTime=txn_time,
                          ta=updatedData.get(f.IDENTIFIER.nm),
                          role=updatedData.get(ROLE),
                          verkey=updatedData.get(VERKEY),
                          isCommitted=isCommitted)

    def hasNym(self, nym, isCommitted: bool = True):
        return self.idrCache.hasNym(nym, isCommitted=isCommitted)

    def _add_default_handlers(self):
        self._add_default_static_validation_handlers()
        self._add_default_dynamic_validation_handlers()
        self._add_default_state_update_handlers()
        self._add_default_post_batch_creation_handlers()
        self._add_default_post_batch_commit_handlers()
        self._add_default_post_batch_rejection_handlers()
        self._add_default_query_handlers()

    def _add_default_static_validation_handlers(self):
        self.add_static_validation_handler(NYM, self._doStaticValidationNym)
        self.add_static_validation_handler(ATTRIB, self._doStaticValidationAttrib)
        self.add_static_validation_handler(GET_REVOC_REG_DELTA, self._doStaticValidationGetRevocRegDelta)

    def add_static_validation_handler(self, txn_type, handler: Callable):
        if txn_type in self.static_validation_handlers:
            raise ValueError('There is already a static validation handler'
                             ' registered for {}'.format(txn_type))
        self.static_validation_handlers[txn_type] = handler

    def _add_default_dynamic_validation_handlers(self):
        self.add_dynamic_validation_handler(NYM, self._validateNym)
        self.add_dynamic_validation_handler(ATTRIB,
                                            self._validateAttrib)
        self.add_dynamic_validation_handler(SCHEMA,
                                            self._validate_schema)
        self.add_dynamic_validation_handler(CLAIM_DEF,
                                            self._validate_claim_def)
        self.add_dynamic_validation_handler(REVOC_REG_DEF,
                                            self._validate_revoc_reg_def)
        self.add_dynamic_validation_handler(REVOC_REG_ENTRY,
                                            self._validate_revoc_reg_entry)

    def add_dynamic_validation_handler(self, txn_type, handler: Callable):
        if txn_type in self.dynamic_validation_handlers:
            raise ValueError('There is already a dynamic validation handler'
                             ' registered for {}'.format(txn_type))
        self.dynamic_validation_handlers[txn_type] = handler

    def _add_default_state_update_handlers(self):
        self.add_state_update_handler(NYM, self._addNym)
        self.add_state_update_handler(ATTRIB, self._addAttr)
        self.add_state_update_handler(SCHEMA, self._addSchema)
        self.add_state_update_handler(CLAIM_DEF, self._addClaimDef)
        self.add_state_update_handler(REVOC_REG_DEF, self._addRevocDef)
        self.add_state_update_handler(REVOC_REG_ENTRY, self._addRevocRegEntry)

    def add_state_update_handler(self, txn_type, handler: Callable):
        if txn_type in self.state_update_handlers:
            raise ValueError('There is already a state update handler registered '
                             'for {}'.format(txn_type))
        self.state_update_handlers[txn_type] = handler

    def _add_default_post_batch_creation_handlers(self):
        self.add_post_batch_creation_handler(self.idrCache.currentBatchCreated)

    def add_post_batch_creation_handler(self, handler: Callable):
        if handler in self.post_batch_creation_handlers:
            raise ValueError('There is already a post batch create handler '
                             'registered {}'.format(handler))
        self.post_batch_creation_handlers.append(handler)

    def _add_default_post_batch_commit_handlers(self):
        self.add_post_batch_commit_handler(self.update_idr_cache)

    def add_post_batch_commit_handler(self, handler: Callable):
        if handler in self.post_batch_commit_handlers:
            raise ValueError('There is already a post batch commit handler '
                             'registered {}'.format(handler))
        self.post_batch_commit_handlers.append(handler)

    def _add_default_post_batch_rejection_handlers(self):
        self.add_post_batch_rejection_handler(self.idrCache.batchRejected)

    def add_post_batch_rejection_handler(self, handler: Callable):
        if handler in self.post_batch_rejection_handlers:
            raise ValueError('There is already a post batch reject handler '
                             'registered {}'.format(handler))
        self.post_batch_rejection_handlers.append(handler)

    def _add_default_query_handlers(self):
        self.add_query_handler(GET_NYM, self.handleGetNymReq)
        self.add_query_handler(GET_ATTR, self.handleGetAttrsReq)
        self.add_query_handler(GET_SCHEMA, self.handleGetSchemaReq)
        self.add_query_handler(GET_CLAIM_DEF, self.handleGetClaimDefReq)
        self.add_query_handler(GET_REVOC_REG_DEF, self.handleGetRevocRegDefReq)
        self.add_query_handler(GET_REVOC_REG, self.handleGetRevocRegReq)
        self.add_query_handler(GET_REVOC_REG_DELTA, self.handleGetRevocRegDelta)

    def add_query_handler(self, txn_type, handler: Callable):
        if txn_type in self.query_handlers:
            raise ValueError('There is already a query handler registered '
                             'for {}'.format(txn_type))
        self.query_handlers[txn_type] = handler

    def handleGetNymReq(self, request: Request):
        nym = request.operation[TARGET_NYM]
        path = domain.make_state_path_for_nym(nym)
        nym_data, proof = self.get_value_from_state(path, with_proof=True)
        if nym_data:
            nym_data = self.stateSerializer.deserialize(nym_data)
            nym_data[TARGET_NYM] = nym
            data = self.stateSerializer.serialize(nym_data)
            seq_no = nym_data[f.SEQ_NO.nm]
            update_time = nym_data[TXN_TIME]
        else:
            data = None
            seq_no = None
            update_time = None

        # TODO: add update time here!
        result = self.make_domain_result(request=request,
                                         data=data,
                                         last_seq_no=seq_no,
                                         update_time=update_time,
                                         proof=proof)

        result.update(request.operation)
        return result

    def handleGetSchemaReq(self, request: Request):
        author_did = get_read_schema_from(request)
        schema_name = get_read_schema_name(request)
        schema_version = get_read_schema_version(request)
        schema, lastSeqNo, lastUpdateTime, proof = self.getSchema(
            author=author_did,
            schemaName=schema_name,
            schemaVersion=schema_version,
            with_proof=True
        )
        # TODO: we have to do this since SCHEMA has a bit different format than other txns
        # (it has NAME and VERSION inside DATA, and it's not part of the state value, but state key)
        if schema is None:
            schema = {}
        schema.update({
            SCHEMA_NAME: schema_name,
            SCHEMA_VERSION: schema_version
        })
        return self.make_domain_result(request=request,
                                       data=schema,
                                       last_seq_no=lastSeqNo,
                                       update_time=lastUpdateTime,
                                       proof=proof)

    def handleGetClaimDefReq(self, request: Request):
        frm = get_read_claim_def_from(request)
        signature_type = get_read_claim_def_signature_type(request)
        schema_ref = get_read_claim_def_schema_ref(request)
        tag = get_read_claim_def_tag(request)
        keys, lastSeqNo, lastUpdateTime, proof = self.getClaimDef(
            author=frm,
            schemaSeqNo=schema_ref,
            signatureType=signature_type,
            tag=tag
        )
        result = self.make_domain_result(request=request,
                                         data=keys,
                                         last_seq_no=lastSeqNo,
                                         update_time=lastUpdateTime,
                                         proof=proof)
        result[CLAIM_DEF_SIGNATURE_TYPE] = signature_type
        return result

    def handleGetRevocRegDefReq(self, request: Request):
        state_path = request.operation.get(ID, None)
        assert state_path
        try:
            keys, last_seq_no, last_update_time, proof = self.lookup(state_path, isCommitted=True, with_proof=True)
        except KeyError:
            keys, last_seq_no, last_update_time, proof = None, None, None, None
        result = self.make_domain_result(request=request,
                                         data=keys,
                                         last_seq_no=last_seq_no,
                                         update_time=last_update_time,
                                         proof=proof)
        return result

    def handleGetRevocRegReq(self, request: Request):
        req_ts = request.operation.get(TIMESTAMP)
        revoc_reg_def_id = request.operation.get(REVOC_REG_DEF_ID)
        # Get root hash corresponding with given timestamp
        past_root = self.ts_store.get_equal_or_prev(req_ts)
        # Path to corresponding ACCUM record in state
        path = domain.make_state_path_for_revoc_reg_entry_accum(revoc_reg_def_id=revoc_reg_def_id)
        entry_state = StateValue()
        if past_root is not None:
            encoded_entry, proof = self.get_value_from_state(path,
                                                             head_hash=past_root,
                                                             with_proof=True)
            entry_state.proof = proof
            if encoded_entry:
                revoc_reg_entry_accum, seq_no, last_update_time = domain.decode_state_value(encoded_entry)
                entry_state = StateValue(root_hash=past_root,
                                         value=revoc_reg_entry_accum,
                                         seq_no=seq_no,
                                         update_time=last_update_time,
                                         proof=proof)

        return self.make_domain_result(request=request,
                                       data=entry_state.value,
                                       last_seq_no=entry_state.seq_no,
                                       update_time=entry_state.update_time,
                                       proof=entry_state.proof)

    def _get_reg_entry_by_timestamp(self, timestamp, path_to_reg_entry):
        reg_entry = None
        seq_no = None
        last_update_time = None
        reg_entry_proof = None
        past_root = self.ts_store.get_equal_or_prev(timestamp)
        if past_root:
            encoded_entry, reg_entry_proof = self.get_value_from_state(path_to_reg_entry,
                                                                       head_hash=past_root,
                                                                       with_proof=True)
            if encoded_entry:
                reg_entry, seq_no, last_update_time = domain.decode_state_value(encoded_entry)
        return StateValue(root_hash=past_root,
                          value=reg_entry,
                          seq_no=seq_no,
                          update_time=last_update_time,
                          proof=reg_entry_proof)

    def _get_reg_entry_accum_by_timestamp(self, timestamp, path_to_reg_entry_accum):
        reg_entry_accum = None
        seq_no = None
        last_update_time = None
        reg_entry_accum_proof = None
        past_root = self.ts_store.get_equal_or_prev(timestamp)
        if past_root:
            encoded_entry, reg_entry_accum_proof = self.get_value_from_state(
                path_to_reg_entry_accum, head_hash=past_root, with_proof=True)
            if encoded_entry:
                reg_entry_accum, seq_no, last_update_time = domain.decode_state_value(encoded_entry)
        return StateValue(root_hash=past_root,
                          value=reg_entry_accum,
                          seq_no=seq_no,
                          update_time=last_update_time,
                          proof=reg_entry_accum_proof)

    def handleGetRevocRegDelta(self, request: Request):
        """
        For getting reply we need:
        1. Get REVOC_REG_ENTRY by "TO" timestamp from state
        2. If FROM is given in request, then Get REVOC_REG_ENTRY by "FROM" timestamp from state
        3. Get ISSUANCE_TYPE for REVOC_REG_DEF (revoked/issued strategy)
        4. Compute issued and revoked indices by corresponding strategy
        5. Make result
           5.1 Now, if "FROM" is presented in request, then STATE_PROOF_FROM and ACCUM (revocation entry for "FROM" timestamp)
               will added into data section
           5.2 If not, then only STATE_PROOF for "TO" revocation entry will added
        :param request:
        :return: Reply
        """
        req_ts_from = request.operation.get(FROM, None)
        req_ts_to = request.operation.get(TO)
        revoc_reg_def_id = request.operation.get(REVOC_REG_DEF_ID)
        reply = None
        """
        Get root hash for "to" timestamp
        Get REVOC_REG_ENTRY and ACCUM record for timestamp "to"
        """
        path_to_reg_entry = domain.make_state_path_for_revoc_reg_entry(revoc_reg_def_id=revoc_reg_def_id)
        path_to_reg_entry_accum = domain.make_state_path_for_revoc_reg_entry_accum(revoc_reg_def_id=revoc_reg_def_id)

        entry_to = self._get_reg_entry_by_timestamp(req_ts_to, path_to_reg_entry)
        accum_to = self._get_reg_entry_accum_by_timestamp(req_ts_to, path_to_reg_entry_accum)
        entry_from = StateValue()
        accum_from = StateValue()

        if accum_to.value and entry_to.value:
            """Get issuance type from REVOC_REG_DEF"""
            encoded_revoc_reg_def = self.state.get_for_root_hash(entry_to.root_hash,
                                                                 revoc_reg_def_id)
            if encoded_revoc_reg_def:
                revoc_reg_def, _, _ = domain.decode_state_value(encoded_revoc_reg_def)
                strategy_cls = self.get_revocation_strategy(revoc_reg_def[VALUE][ISSUANCE_TYPE])
                issued_to = entry_to.value[VALUE].get(ISSUED, [])
                revoked_to = entry_to.value[VALUE].get(REVOKED, [])
                if req_ts_from:
                    """Get REVOC_REG_ENTRY and ACCUM records for timestamp from if exist"""
                    entry_from = self._get_reg_entry_by_timestamp(req_ts_from, path_to_reg_entry)
                    accum_from = self._get_reg_entry_accum_by_timestamp(req_ts_from, path_to_reg_entry_accum)
                if req_ts_from and entry_from.value and accum_from.value:
                    """Compute issued/revoked lists corresponding with ISSUANCE_TYPE strategy"""
                    issued_from = entry_from.value[VALUE].get(ISSUED, [])
                    revoked_from = entry_from.value[VALUE].get(REVOKED, [])
                    result_issued, result_revoked = strategy_cls.get_delta({ISSUED: issued_to,
                                                                            REVOKED: revoked_to},
                                                                           {ISSUED: issued_from,
                                                                            REVOKED: revoked_from})
                else:
                    result_issued, result_revoked = strategy_cls.get_delta({ISSUED: issued_to,
                                                                            REVOKED: revoked_to},
                                                                           None)
                reply = {
                    REVOC_REG_DEF_ID: revoc_reg_def_id,
                    REVOC_TYPE: revoc_reg_def.get(REVOC_TYPE),
                    VALUE: {
                        ACCUM_TO: accum_to.value if entry_from.value else entry_to.value,
                        ISSUED: result_issued,
                        REVOKED: result_revoked
                    }

                }
                """If we got "from" timestamp, then add state proof into "data" section of reply"""
                if req_ts_from and accum_from.value:
                    reply[STATE_PROOF_FROM] = accum_from.proof
                    reply[VALUE][ACCUM_FROM] = accum_from.value

        if accum_to and entry_to:
            seq_no = accum_to.seq_no if entry_from.value else entry_to.seq_no
            update_time = accum_to.update_time if entry_from.value else entry_to.update_time
            proof = accum_to.proof if entry_from.value else entry_to.proof
        else:
            seq_no = None
            update_time = None
            proof = None

        return self.make_domain_result(request=request,
                                       data=reply,
                                       last_seq_no=seq_no,
                                       update_time=update_time,
                                       proof=proof)

    def handleGetAttrsReq(self, request: Request):
        if not self._validate_attrib_keys(request.operation):
            raise InvalidClientRequest(request.identifier, request.reqId,
                                       '{} should have one and only one of '
                                       '{}, {}, {}'
                                       .format(ATTRIB, RAW, ENC, HASH))
        nym = request.operation[TARGET_NYM]
        if RAW in request.operation:
            attr_type = RAW
        elif ENC in request.operation:
            # If attribute is encrypted, it will be queried by its hash
            attr_type = ENC
        else:
            attr_type = HASH
        attr_key = request.operation[attr_type]
        value, lastSeqNo, lastUpdateTime, proof = \
            self.getAttr(did=nym, key=attr_key, attr_type=attr_type)
        attr = None
        if value is not None:
            if HASH in request.operation:
                attr = attr_key
            else:
                attr = value
        return self.make_domain_result(request=request,
                                       data=attr,
                                       last_seq_no=lastSeqNo,
                                       update_time=lastUpdateTime,
                                       proof=proof)

    def lookup(self, path, isCommitted=True, with_proof=False) -> (str, int):
        """
        Queries state for data on specified path

        :param path: path to data
        :param isCommitted: queries the committed state root if True else the uncommitted root
        :param with_proof: creates proof if True
        :return: data
        """
        assert path is not None
        head_hash = self.state.committedHeadHash if isCommitted else self.state.headHash
        encoded, proof = self.get_value_from_state(path, head_hash, with_proof=with_proof)
        if encoded:
            value, last_seq_no, last_update_time = domain.decode_state_value(encoded)
            return value, last_seq_no, last_update_time, proof
        return None, None, None, proof

    def _addNym(self, txn, isCommitted=False) -> None:
        txn_data = get_payload_data(txn)
        nym = txn_data.get(TARGET_NYM)
        data = {
            f.IDENTIFIER.nm: get_from(txn),
            f.SEQ_NO.nm: get_seq_no(txn),
            TXN_TIME: get_txn_time(txn)
        }
        if ROLE in txn_data:
            data[ROLE] = txn_data.get(ROLE)
        if VERKEY in txn_data:
            data[VERKEY] = txn_data.get(VERKEY)
        self.updateNym(nym, txn, isCommitted=isCommitted)

    def _addAttr(self, txn, isCommitted=False) -> None:
        """
        The state trie stores the hash of the whole attribute data at:
            the did+attribute name if the data is plaintext (RAW)
            the did+hash(attribute) if the data is encrypted (ENC)
        If the attribute is HASH, then nothing is stored in attribute store,
        the trie stores a blank value for the key did+hash
        """
        assert get_type(txn) == ATTRIB
        attr_type, path, value, hashed_value, value_bytes = domain.prepare_attr_for_state(txn)
        self.state.set(path, value_bytes)
        if attr_type != HASH:
            self.attributeStore.set(hashed_value, value)

    def _addSchema(self, txn, isCommitted=False) -> None:
        assert get_type(txn) == SCHEMA
        path, value_bytes = domain.prepare_schema_for_state(txn)
        self.state.set(path, value_bytes)

    def _addClaimDef(self, txn, isCommitted=False) -> None:
        assert get_type(txn) == CLAIM_DEF
        path, value_bytes = domain.prepare_claim_def_for_state(txn)
        self.state.set(path, value_bytes)

    def _addRevocDef(self, txn, isCommitted=False) -> None:
        assert get_type(txn) == REVOC_REG_DEF
        path, value_bytes = domain.prepare_revoc_def_for_state(txn)
        self.state.set(path, value_bytes)

    def _addRevocRegEntry(self, txn, isCommitted=False) -> None:
        current_entry, revoc_def = self._get_current_revoc_entry_and_revoc_def(
            author_did=get_from(txn),
            revoc_reg_def_id=get_payload_data(txn)[REVOC_REG_DEF_ID],
            req_id=get_req_id(txn)
        )
        writer_cls = self.get_revocation_strategy(
            revoc_def[VALUE][ISSUANCE_TYPE])
        writer = writer_cls(self.state)
        writer.write(current_entry, txn)

    def onBatchCreated(self, stateRoot, txnTime):
        for handler in self.post_batch_creation_handlers:
            handler(stateRoot, txnTime)

    def onBatchRejected(self):
        for handler in self.post_batch_rejection_handlers:
            handler()

    def onBatchCommitted(self, stateRoot):
        for handler in self.post_batch_commit_handlers:
            handler(stateRoot)

    def getAttr(self,
                did: str,
                key: str,
                attr_type,
                isCommitted=True) -> (str, int, int, list):
        assert did is not None
        assert key is not None
        path = domain.make_state_path_for_attr(did, key, attr_type == HASH)
        try:
            hashed_val, lastSeqNo, lastUpdateTime, proof = \
                self.lookup(path, isCommitted, with_proof=True)
        except KeyError:
            return None, None, None, None
        if not hashed_val or hashed_val == '':
            # Its a HASH attribute
            return hashed_val, lastSeqNo, lastUpdateTime, proof
        else:
            try:
                value = self.attributeStore.get(hashed_val)
            except KeyError:
                logger.error('Could not get value from attribute store for {}'
                             .format(hashed_val))
                return None, None, None, None
        return value, lastSeqNo, lastUpdateTime, proof

    def getSchema(self,
                  author: str,
                  schemaName: str,
                  schemaVersion: str,
                  isCommitted=True,
                  with_proof=True) -> (str, int, int, list):
        assert author is not None
        assert schemaName is not None
        assert schemaVersion is not None
        path = domain.make_state_path_for_schema(author, schemaName, schemaVersion)
        try:
            keys, seqno, lastUpdateTime, proof = self.lookup(path, isCommitted, with_proof=with_proof)
            return keys, seqno, lastUpdateTime, proof
        except KeyError:
            return None, None, None, None

    def getClaimDef(self,
                    author: str,
                    schemaSeqNo: str,
                    signatureType,
                    tag,
                    isCommitted=True) -> (str, int, int, list):
        assert author is not None
        assert schemaSeqNo is not None
        path = domain.make_state_path_for_claim_def(author, schemaSeqNo, signatureType, tag)
        try:
            keys, seqno, lastUpdateTime, proof = self.lookup(path, isCommitted, with_proof=True)
            return keys, seqno, lastUpdateTime, proof
        except KeyError:
            return None, None, None, None

    def getRevocDef(self,
                    author_did,
                    cred_def_id,
                    revoc_def_type,
                    revoc_def_tag,
                    isCommitted=True) -> (str, int, int, list):
        assert author_did is not None
        assert cred_def_id is not None
        assert revoc_def_type is not None
        assert revoc_def_tag is not None
        path = domain.make_state_path_for_revoc_def(author_did,
                                                    cred_def_id,
                                                    revoc_def_type,
                                                    revoc_def_tag)
        try:
            keys, seqno, lastUpdateTime, proof = self.lookup(path, isCommitted, with_proof=True)
            return keys, seqno, lastUpdateTime, proof
        except KeyError:
            return None, None, None, None

    def getRevocDefEntry(self,
                         revoc_reg_def_id,
                         isCommitted=True) -> (str, int, int, list):
        assert revoc_reg_def_id
        path = domain.make_state_path_for_revoc_reg_entry(revoc_reg_def_id=revoc_reg_def_id)
        try:
            keys, seqno, lastUpdateTime, proof = self.lookup(path, isCommitted, with_proof=False)
            return keys, seqno, lastUpdateTime, proof
        except KeyError:
            return None, None, None, None

    def get_revocation_strategy(self, typ):
        return self.revocation_strategy_map.get(typ)

    def get_query_response(self, request: Request):
        return self.query_handlers[request.operation[TXN_TYPE]](request)

    @staticmethod
    def transform_txn_for_ledger(txn):
        """
        Some transactions need to be transformed before they can be stored in the
        ledger, eg. storing certain payload in another data store and only its
        hash in the ledger
        """
        if get_type(txn) == ATTRIB:
            txn = DomainReqHandler.transform_attrib_for_ledger(txn)
        return txn

    @staticmethod
    def transform_attrib_for_ledger(txn):
        """
        Creating copy of result so that `RAW`, `ENC` or `HASH` can be
        replaced by their hashes. We do not insert actual attribute data
        in the ledger but only the hash of it.
        """
        txn = deepcopy(txn)
        txn_data = get_payload_data(txn)
        attr_type, _, value = domain.parse_attr_txn(txn_data)
        if attr_type in [RAW, ENC]:
            txn_data[attr_type] = domain.hash_of(value) if value else ''

        return txn
