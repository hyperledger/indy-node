from typing import Optional

from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit

from indy_common.config_util import getConfig

from indy_common.constants import CONFIG_LEDGER_ID, POOL_UPGRADE, \
    ACTION, CANCEL, START, SCHEDULE, PACKAGE, REINSTALL

from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_node.server.upgrader import Upgrader
from plenum.common.constants import FORCE, VERSION, NAME
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_request_data, get_payload_data
from plenum.server.database_manager import DatabaseManager
from plenum.server.pool_manager import TxnPoolManager
from plenum.server.request_handlers.handler_interfaces.write_request_handler import WriteRequestHandler


class PoolUpgradeHandler(WriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 upgrader: Upgrader,
                 write_req_validator: WriteRequestValidator,
                 pool_manager: TxnPoolManager):
        super().__init__(database_manager, POOL_UPGRADE, CONFIG_LEDGER_ID)
        self.upgrader = upgrader
        self.write_req_validator = write_req_validator
        self.pool_manager = pool_manager

    def static_validation(self, request: Request):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)
        action = operation.get(ACTION)
        if action not in (START, CANCEL):
            raise InvalidClientRequest(identifier, req_id,
                                       "{} not a valid action".
                                       format(action))
        if action == START:
            schedule = operation.get(SCHEDULE, {})
            force = operation.get(FORCE)
            force = str(force) == 'True'
            isValid, msg = self.upgrader.isScheduleValid(
                schedule, self.pool_manager.getNodesServices(), force)
            if not isValid:
                raise InvalidClientRequest(identifier, req_id,
                                           "{} not a valid schedule since {}".
                                           format(schedule, msg))

    def dynamic_validation(self, request: Request, req_pp_time: Optional[int]):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)
        status = '*'

        pkg_to_upgrade = operation.get(PACKAGE, getConfig().UPGRADE_ENTRY)
        targetVersion = operation[VERSION]
        reinstall = operation.get(REINSTALL, False)

        if not pkg_to_upgrade:
            raise InvalidClientRequest(identifier, req_id, "Upgrade package name is empty")

        try:
            res = self.upgrader.check_upgrade_possible(pkg_to_upgrade, targetVersion, reinstall)
        except Exception as exc:
            res = str(exc)

        if res:
            raise InvalidClientRequest(identifier, req_id, res)

        action = operation.get(ACTION)
        # TODO: Some validation needed for making sure name and version
        # present
        txn = self.upgrader.get_upgrade_txn(
            lambda txn: get_payload_data(txn).get(
                NAME,
                None) == operation.get(
                NAME,
                None) and get_payload_data(txn).get(VERSION) == operation.get(VERSION),
            reverse=True)
        if txn:
            status = get_payload_data(txn).get(ACTION, '*')

        if status == START and action == START:
            raise InvalidClientRequest(
                identifier,
                req_id,
                "Upgrade '{}' is already scheduled".format(
                    operation.get(NAME)))
        if status == '*':
            auth_action = AuthActionAdd(txn_type=POOL_UPGRADE,
                                        field=ACTION,
                                        value=action)
        else:
            auth_action = AuthActionEdit(txn_type=POOL_UPGRADE,
                                         field=ACTION,
                                         old_value=status,
                                         new_value=action)
        self.write_req_validator.validate(request,
                                          [auth_action])

    def apply_forced_request(self, req: Request):
        super().apply_forced_request(req)
        txn = self._req_to_txn(req)
        self.upgrader.handleUpgradeTxn(txn)

    # Config handler don't use state for any validation for now
    def update_state(self, txn, prev_result, request, is_committed=False):
        pass
