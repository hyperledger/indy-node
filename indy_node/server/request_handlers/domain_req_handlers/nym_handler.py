from binascii import hexlify

from common.serializers.serialization import domain_state_serializer
from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_common.state import domain
from indy_common.constants import NYM
from indy_common.auth import Authoriser
from ledger.util import F

from plenum.common.constants import ROLE, TARGET_NYM, VERKEY, DOMAIN_LEDGER_ID, TXN_TIME
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_payload_data, get_seq_no, get_txn_time, get_request_data, get_from
from plenum.common.types import f
from plenum.server.database_manager import DatabaseManager
from plenum.server.request_handlers.utils import nym_to_state_key, get_nym_details
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class NymHandler(WriteRequestHandler):
    state_serializer = domain_state_serializer

    def __init__(self, database_manager: DatabaseManager,
                 write_request_validator: WriteRequestValidator):
        super().__init__(database_manager, NYM, DOMAIN_LEDGER_ID)
        self.write_request_validator = write_request_validator

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

    def dynamic_validation(self, request: Request):
        self._validate_request_type(request)
        operation = request.operation

        nym_data = self.database_manager.idr_cache.getNym(operation[TARGET_NYM], isCommitted=False)
        if not nym_data:
            # If nym does not exist
            self._validate_new_nym(request, operation)
        else:
            self._validate_existing_nym(request, operation, nym_data)

    def gen_state_key(self, txn):
        self._validate_txn_type(txn)
        nym = get_payload_data(txn).get(TARGET_NYM)
        binary_digest = domain.make_state_path_for_nym(nym)
        return hexlify(binary_digest).decode()

    def update_state(self, txn, prev_result, is_committed=False):
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
        new_data[F.seqNo.name] = get_seq_no(txn)
        new_data[TXN_TIME] = get_txn_time(txn)
        existing_data.update(new_data)
        val = self.state_serializer.serialize(existing_data)
        key = nym_to_state_key(nym)
        self.state.set(key, val)
        return existing_data

    def _validate_new_nym(self, request, operation):
        role = operation.get(ROLE)
        self.write_request_validator.validate(request,
                                              [AuthActionAdd(txn_type=NYM,
                                                             field=ROLE,
                                                             value=role)])

    def _validate_existing_nym(self, request, operation, nym_data):
        origin = request.identifier
        owner = self.database_manager.idr_cache.getOwnerFor(operation[TARGET_NYM], isCommitted=False)
        is_owner = origin == owner

        updateKeys = [ROLE, VERKEY]
        for key in updateKeys:
            if key in operation:
                newVal = operation[key]
                oldVal = nym_data.get(key)
                self.write_request_validator.validate(request,
                                                      [AuthActionEdit(txn_type=NYM,
                                                                      field=key,
                                                                      old_value=oldVal,
                                                                      new_value=newVal,
                                                                      is_owner=is_owner)])
