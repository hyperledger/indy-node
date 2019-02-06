from indy_common.authorize.auth_actions import AuthActionAdd, AuthActionEdit
from indy_node.server.request_handlers.config_req_handlers.config_write_request_handler import ConfigWriteRequestHandler
from indy_node.utils.node_control_utils import NodeControlUtil

from indy_common.config_util import getConfig

from indy_common.constants import CONFIG_LEDGER_ID, POOL_UPGRADE, \
    ACTION, CANCEL, START, SCHEDULE, PACKAGE, APP_NAME, REINSTALL

from indy_common.authorize.auth_request_validator import WriteRequestValidator
from indy_node.server.upgrader import Upgrader
from plenum.common.constants import FORCE, VERSION, NAME
from plenum.common.exceptions import InvalidClientRequest
from plenum.common.request import Request
from plenum.common.txn_util import get_request_data, get_payload_data
from plenum.server.database_manager import DatabaseManager
from plenum.server.pool_manager import TxnPoolManager


class PoolUpgradeHandler(ConfigWriteRequestHandler):

    def __init__(self, database_manager: DatabaseManager,
                 upgrader: Upgrader,
                 write_request_validator: WriteRequestValidator,
                 pool_manager: TxnPoolManager):
        super().__init__(database_manager, POOL_UPGRADE, CONFIG_LEDGER_ID)
        self.upgrader = upgrader
        self.write_request_validator = write_request_validator
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

    def dynamic_validation(self, request: Request):
        self._validate_request_type(request)
        identifier, req_id, operation = get_request_data(request)
        status = '*'
        pkt_to_upgrade = operation.get(PACKAGE, getConfig().UPGRADE_ENTRY)
        if pkt_to_upgrade:
            currentVersion, cur_deps = self.curr_pkt_info(pkt_to_upgrade)
            if not currentVersion:
                raise InvalidClientRequest(identifier, req_id,
                                           "Packet {} is not installed and cannot be upgraded".
                                           format(pkt_to_upgrade))
            if all([APP_NAME not in d for d in cur_deps]):
                raise InvalidClientRequest(identifier, req_id,
                                           "Packet {} doesn't belong to pool".format(pkt_to_upgrade))
        else:
            raise InvalidClientRequest(identifier, req_id, "Upgrade packet name is empty")

        targetVersion = operation[VERSION]
        reinstall = operation.get(REINSTALL, False)
        if not Upgrader.is_version_upgradable(currentVersion, targetVersion, reinstall):
            # currentVersion > targetVersion
            raise InvalidClientRequest(identifier, req_id, "Version is not upgradable")

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
        self.write_request_validator.validate(request,
                                              [auth_action])

    def apply_forced_request(self, req: Request):
        super().apply_forced_request(req)
        txn = self._req_to_txn(req)
        self.upgrader.handleUpgradeTxn(txn)

    def curr_pkt_info(self, pkg_name):
        if pkg_name == APP_NAME:
            return Upgrader.getVersion(), [APP_NAME]
        return NodeControlUtil.curr_pkt_info(pkg_name)

    # Config handler don't use state for any validation for now
    def update_state(self, txn, prev_result, is_committed=False):
        pass

    def gen_state_key(self, txn):
        pass
