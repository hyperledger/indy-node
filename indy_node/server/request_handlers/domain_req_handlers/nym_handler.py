from binascii import hexlify
from hashlib import sha256
import json
from typing import Optional
import base58

from common.serializers.serialization import domain_state_serializer
from indy_common.auth import Authoriser
from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.base_diddoc_template import BaseDIDDoc

# TODO - Import DIDDOC_CONTENT from plenum?
from indy_common.constants import NYM, DIDDOC_CONTENT

# TODO - Improve exception with reason
from indy_common.exceptions import InvalidDIDDocException
from ledger.util import F
from plenum.common.constants import ROLE, TARGET_NYM, TXN_TIME, VERKEY
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import (
    get_from,
    get_payload_data,
    get_request_data,
    get_seq_no,
    get_txn_time,
)
from plenum.common.types import f
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.nym_handler import NymHandler as PNymHandler
from plenum.server.request_handlers.utils import get_nym_details, nym_to_state_key

# TODO - Clean up
DID_CONTEXT = "https://www.w3.org/ns/did/v1"


class NymHandler(PNymHandler):
    state_serializer = domain_state_serializer

    def __init__(self, config, database_manager: DatabaseManager,
                 write_req_validator: WriteRequestValidator):
        super().__init__(config, database_manager)
        self.write_req_validator = write_req_validator
        self.namespace = config.NETWORK_NAME

    def static_validation(self, request: Request):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)
        role = operation.get(ROLE)
        nym = operation.get(TARGET_NYM)
        if isinstance(nym, str):
            nym = nym.strip()
        if not nym:
            raise InvalidClientRequest(identifier, req_id,
                                       "{} needs to be present".
                                       format(TARGET_NYM))
        if not Authoriser.isValidRole(role):
            raise InvalidClientRequest(identifier, req_id,
                                       "{} not a valid role".
                                       format(role))

        diddoc_content = operation.get(DIDDOC_CONTENT, None)
        if diddoc_content:
            diddoc_content = json.loads(diddoc_content)
            try:
                self._validate_diddoc_content(diddoc_content)
            except InvalidDIDDocException:
                raise InvalidClientRequest(
                    identifier,
                    req_id,
                    "Invalid DIDDOC_Content",
                )

    def additional_dynamic_validation(
        self, request: Request, req_pp_time: Optional[int]
    ):
        self._validate_request_type(request)
        operation = request.operation

        nym_data = self.database_manager.idr_cache.getNym(operation[TARGET_NYM], isCommitted=False)
        if not nym_data:
            # If nym does not exist
            self._validate_new_nym(request, operation)
        else:
            self._validate_existing_nym(request, operation, nym_data)

    def gen_txn_id(self, txn):
        self._validate_txn_type(txn)
        nym = get_payload_data(txn).get(TARGET_NYM)
        binary_digest = self.make_state_path_for_nym(nym)
        return hexlify(binary_digest).decode()

    def update_state(self, txn, prev_result, request, is_committed=False):
        self._validate_txn_type(txn)
        nym = get_payload_data(txn).get(TARGET_NYM)
        existing_data = get_nym_details(self.state, nym,
                                        is_committed=is_committed)
        txn_data = get_payload_data(txn)
        new_data = {}
        if not existing_data:
            new_data[f.IDENTIFIER.nm] = get_from(txn)
            new_data[ROLE] = None
            new_data[VERKEY] = None

        if ROLE in txn_data:
            new_data[ROLE] = txn_data[ROLE]
        if VERKEY in txn_data:
            new_data[VERKEY] = txn_data[VERKEY]
        if DIDDOC_CONTENT in txn_data:
            new_data[DIDDOC_CONTENT] = txn_data[DIDDOC_CONTENT]
        new_data[F.seqNo.name] = get_seq_no(txn)
        new_data[TXN_TIME] = get_txn_time(txn)
        existing_data.update(new_data)
        val = self.state_serializer.serialize(existing_data)
        key = nym_to_state_key(nym)
        self.state.set(key, val)
        return existing_data

    def _validate_new_nym(self, request, operation):
        identifier, req_id, _ = get_request_data(request)
        role = operation.get(ROLE)

        nym_data = self.database_manager.idr_cache.getNym(
            request.identifier, isCommitted=False
        )

        nym_data = self.database_manager.idr_cache.getNym(request.identifier, isCommitted=False)
        if not nym_data:
            # Non-ledger nym case. These two checks duplicated and mainly executed in client_authn,
            # but it has point to repeat them here, for clear understanding of validation non-ledger request cases.
            if request.identifier != request.operation.get(TARGET_NYM):
                raise InvalidClientRequest(identifier, req_id, "DID which is not stored on ledger can "
                                                               "send nym txn only if appropriate auth_rules set "
                                                               "and sender did equal to destination nym")
            if not request.operation.get(VERKEY):
                raise InvalidClientRequest(
                    identifier,
                    req_id,
                    "Non-ledger nym txn must contain verkey for new did",
                )

        if self.config.ENABLE_DID_INDY and not self._is_self_certifying(
            request.operation.get(TARGET_NYM), request.operation.get(VERKEY)
        ):
            raise InvalidClientRequest(
                identifier,
                req_id,
                "DID is not self-certifying; must be first 16 bytes of SHA256 of verkey",
            )

        self.write_req_validator.validate(
            request, [AuthActionAdd(txn_type=NYM, field=ROLE, value=role)]
        )

    def _validate_existing_nym(self, request, operation, nym_data):
        origin = request.identifier
        owner = self.database_manager.idr_cache.getOwnerFor(operation[TARGET_NYM], isCommitted=False)
        is_owner = origin == owner

        updateKeys = [ROLE, VERKEY]
        updateKeysInOperationOrOwner = is_owner
        for key in updateKeys:
            if key in operation:
                updateKeysInOperationOrOwner = True
                newVal = operation[key]
                oldVal = nym_data.get(key)
                self.write_req_validator.validate(request,
                                                  [AuthActionEdit(txn_type=NYM,
                                                                  field=key,
                                                                  old_value=oldVal,
                                                                  new_value=newVal,
                                                                  is_owner=is_owner)])
        if not updateKeysInOperationOrOwner:
            raise InvalidClientRequest(request.identifier, request.reqId)

    def _decode_state_value(self, encoded):
        if encoded:
            return domain_state_serializer.deserialize(encoded)
        return None, None, None

    def _is_self_certifying(self, did, verkey):
        # DID must be the base58 encoded first 16 bytes of the 32 bytes verkey
        # See https://hyperledger.github.io/indy-did-method/#creation

        # Previously, it was possible to abbreviate the verification key sent
        # in a nym transaction. Since the DID is now the first 16 bytes of the
        # hash of the full verkey, this abberviation is no longer possible.

        return did == base58.b58encode(
            sha256(base58.b58decode(verkey)).digest()[:16]
        ).decode("utf-8")

    def _validate_diddoc_content(self, diddoc):

        # Must not have an id property
        if diddoc.get("id", None):
            raise InvalidDIDDocException

        context = diddoc.get("@context", None)
        if context:
            # Must be string or array and contain DID_CONTEXT
            if not isinstance(context, (list, str)):
                raise InvalidDIDDocException
            if isinstance(context, str) and not context == DID_CONTEXT:
                raise InvalidDIDDocException
            elif isinstance(context, list) and DID_CONTEXT not in context:
                raise InvalidDIDDocException

        # No element in diddoc is allowed to have same id as verkey in base diddoc
        # Alernative would be to merge with base did doc and perform generic did doc validation,
        # e.g. using pyDID
        for el in diddoc.values():
            if isinstance(el, list):
                for item in el:
                    if self._has_same_id_fragment(item, "verkey"):
                        raise InvalidDIDDocException

    def _has_same_id_fragment(self, item, fragment):

        return (
            isinstance(item, dict) and "id" in item and item["id"].partition("#")[2] == fragment
        )

    # Currently not used
    def _make_base_diddoc(self, request: Request):

        dest = request.operation.get(TARGET_NYM)
        verkey = request.operation.get(VERKEY)

        diddoc = BaseDIDDoc(self.config.NETWORK_NAME, dest, verkey)

        return diddoc
