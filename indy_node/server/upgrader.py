import os
import asyncio
from datetime import datetime
from functools import partial
from typing import Union, Optional, Callable, Dict

import dateutil.parser
import dateutil.tz

from indy_node.server.node_maintainer import NodeMaintainer, \
    NodeControlToolMessage
from plenum.common.txn_util import is_forced, get_seq_no, get_type, get_payload_data, get_req_id, get_from
from stp_core.common.log import getlogger
from plenum.common.constants import VERSION
from common.version import (
    SourceVersion, InvalidVersionError
)

from indy_common.constants import ACTION, POOL_UPGRADE, START, SCHEDULE, \
    CANCEL, JUSTIFICATION, TIMEOUT, REINSTALL, NODE_UPGRADE, \
    UPGRADE_MESSAGE, PACKAGE, APP_NAME
from indy_common.version import src_version_cls
from indy_node.server.upgrade_log import UpgradeLogData, UpgradeLog
from indy_node.utils.node_control_utils import NodeControlUtil

logger = getlogger()


class Upgrader(NodeMaintainer):

    def __init__(self, nodeId, nodeName, dataDir, config, ledger=None,
                 actionLog=None, actionFailedCallback: Callable = None,
                 action_start_callback: Callable = None):
        self._should_notify_about_upgrade = False
        super().__init__(nodeId, nodeName, dataDir, config, ledger, actionLog,
                         actionFailedCallback, action_start_callback)

    @staticmethod
    def get_src_version(
            pkg_name: str = APP_NAME,
            nocache: bool = False) -> SourceVersion:

        if pkg_name == APP_NAME and not nocache:
            from indy_node.__metadata__ import __version__
            return src_version_cls(APP_NAME)(__version__)

        curr_pkg_ver, _ = NodeControlUtil.curr_pkg_info(pkg_name)
        return curr_pkg_ver.upstream if curr_pkg_ver else None

    @staticmethod
    def is_version_upgradable(
            old: SourceVersion, new: SourceVersion, reinstall: bool = False):
        return (new > old) or (new == old and reinstall)

    @staticmethod
    def get_action_id(txn):
        seq_no = get_seq_no(txn) or ''
        if is_forced(txn):
            seq_no = ''
        return '{}{}'.format(get_req_id(txn), seq_no)

    # implements legacy logic used only by migration logic,
    # please use Version classes in code instead
    # TODO refactor migration logic to get rid of that API usage
    @staticmethod
    def compareVersions(verA: str, verB: str) -> int:
        version_cls = src_version_cls(APP_NAME)
        return version_cls.cmp(version_cls(verA), version_cls(verB))

    def _defaultLog(self, dataDir, config):
        log = os.path.join(dataDir, config.upgradeLogFile)
        return UpgradeLog(file_path=log)

    def _is_action_started(self):
        last_action = self.lastActionEventInfo
        if not last_action:
            logger.debug('Node {} has no upgrade events'.format(self.nodeName))
            return False

        if last_action.ev_type != UpgradeLog.Events.started:
            logger.debug(
                "Upgrade for node {} was not scheduled. "
                "Last event is {}"
                .format(self.nodeName, last_action))
            return False

        return True

    def _update_action_log_for_started_action(self):
        ev_data = self.lastActionEventInfo.data

        self._should_notify_about_upgrade = True
        if not self.didLastExecutedUpgradeSucceeded:
            self._actionLog.append_failed(ev_data)
            self._action_failed(ev_data, external_reason=True)
            return

        self._actionLog.append_succeeded(ev_data)
        logger.info(
            "Node '{}' successfully upgraded to version {}"
            .format(self.nodeName, ev_data.version))
        self._notifier.sendMessageUponNodeUpgradeComplete(
            "Upgrade of package {} on node '{}' to version {} scheduled on {} "
            " with upgrade_id {} completed successfully"
            .format(ev_data.pkg_name, self.nodeName,
                    ev_data.version, ev_data.when, ev_data.upgrade_id))

    def should_notify_about_upgrade_result(self):
        # do not rely on NODE_UPGRADE txn in config ledger, since in
        # some cases (for example, when
        # we run POOL_UPGRADE with force=true), we may not have
        # IN_PROGRESS NODE_UPGRADE in the ledger.

        # send NODE_UPGRADE txn only if we were in Upgrade Started
        # state at the very beginning (after Node restarted)
        return self._should_notify_about_upgrade

    def notified_about_action_result(self):
        self._should_notify_about_upgrade = False

    def get_last_node_upgrade_txn(self, start_no: int = None):
        return self.get_upgrade_txn(
            lambda txn: get_type(txn) == NODE_UPGRADE and get_from(txn) == self.nodeId,
            start_no=start_no,
            reverse=True)

    def get_upgrade_txn(self, predicate: Callable = None, start_no: int = None,
                        reverse: bool = False) -> Optional[Dict]:
        def txn_filter(txn):
            return not predicate or predicate(txn)

        def traverse_end_condition(seq_no):
            if reverse:
                return seq_no > 0
            return seq_no <= len(self.ledger)

        inc = 1
        init_start_no = 1
        if reverse:
            inc = -1
            init_start_no = len(self.ledger)

        seq_no = start_no if start_no is not None else init_start_no
        while traverse_end_condition(seq_no):
            txn = self.ledger.getBySeqNo(seq_no)
            if txn_filter(txn):
                return txn
            seq_no += inc
        return None

    # TODO: PoolConfig and Updater both read config ledger independently
    def processLedger(self) -> None:
        """
        Checks ledger for planned but not yet performed upgrades
        and schedules upgrade for the most recent one

        Assumption: Only version is enough to identify a release, no hash
        checking is done
        :return:
        """
        logger.debug(
            '{} processing config ledger for any upgrades'.format(self))
        last_pool_upgrade_txn_start = self.get_upgrade_txn(
            lambda txn: get_type(txn) == POOL_UPGRADE and get_payload_data(txn)[ACTION] == START, reverse=True)
        if last_pool_upgrade_txn_start:
            logger.info('{} found upgrade START txn {}'.format(
                self, last_pool_upgrade_txn_start))
            last_pool_upgrade_txn_seq_no = get_seq_no(last_pool_upgrade_txn_start)

            # searching for CANCEL for this upgrade submitted after START txn
            last_pool_upgrade_txn_cancel = self.get_upgrade_txn(
                lambda txn:
                get_type(txn) == POOL_UPGRADE and get_payload_data(txn)[ACTION] == CANCEL and
                get_payload_data(txn)[VERSION] == get_payload_data(last_pool_upgrade_txn_start)[VERSION],
                start_no=last_pool_upgrade_txn_seq_no + 1)
            if last_pool_upgrade_txn_cancel:
                logger.info('{} found upgrade CANCEL txn {}'.format(
                    self, last_pool_upgrade_txn_cancel))
                return

            self.handleUpgradeTxn(last_pool_upgrade_txn_start)

    # TODO might necessary to improve tests
    @property
    def didLastExecutedUpgradeSucceeded(self) -> bool:
        """
        Checks last record in upgrade log to find out whether it
        is about scheduling upgrade. If so - checks whether current version
        is equals to the one in that record

        :returns: upgrade execution result
        """
        lastEventInfo = self.lastActionEventInfo
        if lastEventInfo:
            ev_data = lastEventInfo.data
            currentPkgVersion = NodeControlUtil.curr_pkg_info(ev_data.pkg_name)[0]
            if currentPkgVersion:
                return currentPkgVersion.upstream == ev_data.version
            else:
                logger.warning(
                    "{} failed to get information about package {} "
                    "scheduled for last upgrade"
                    .format(self, ev_data.pkg_name)
                )
        return False

    @staticmethod
    def check_upgrade_possible(
            pkg_name: str,
            target_ver: str,
            reinstall: bool = False
    ):
        version_cls = src_version_cls(pkg_name)

        try:
            target_ver = version_cls(target_ver)
        except InvalidVersionError as exc:
            return (
                "invalid target version {} for version class {}: "
                .format(target_ver, version_cls, exc)
            )

        # get current installed package version of pkg_name
        curr_pkg_ver, cur_deps = NodeControlUtil.curr_pkg_info(pkg_name)
        if not curr_pkg_ver:
            return ("package {} is not installed and cannot be upgraded"
                    .format(pkg_name))

        # TODO weak check
        if (APP_NAME not in pkg_name and
                all([APP_NAME not in d for d in cur_deps])):
            return "Package {} doesn't belong to pool".format(pkg_name)

        # compare whether it makes sense to try (target >= current, = for reinstall)
        if not Upgrader.is_version_upgradable(
                curr_pkg_ver.upstream, target_ver, reinstall):
            return "Version {} is not upgradable".format(target_ver)

        # get the most recent version of the package for provided version
        # TODO request to NodeControlTool since Node likely runs under user
        # which doesn't have rights to update list of system packages available
        # target_pkg_ver = NodeControlUtil.get_latest_pkg_version(
        #    pkg_name, upstream=target_ver)

        # if not target_pkg_ver:
        #    return ("package {} for target version {} is not found"
        #            .format(pkg_name, target_ver))

        return None

    def handleUpgradeTxn(self, txn) -> None:
        """
        Handles transaction of type POOL_UPGRADE
        Can schedule or cancel upgrade to a newer
        version at specified time

        :param txn:
        """
        FINALIZING_EVENT_TYPES = [UpgradeLog.Events.succeeded, UpgradeLog.Events.failed]

        if get_type(txn) != POOL_UPGRADE:
            return

        logger.info("Node '{}' handles upgrade txn {}".format(self.nodeName, txn))
        txn_data = get_payload_data(txn)
        action = txn_data[ACTION]
        version = txn_data[VERSION]
        justification = txn_data.get(JUSTIFICATION)
        pkg_name = txn_data.get(PACKAGE, self.config.UPGRADE_ENTRY)
        upgrade_id = self.get_action_id(txn)

        # TODO test
        try:
            version = src_version_cls(pkg_name)(version)
        except InvalidVersionError as exc:
            logger.warning(
                "{} can't handle upgrade txn with version {} for package {}: {}"
                .format(self, version, pkg_name, exc)
            )
            return

        if action == START:
            # forced txn could have partial schedule list
            if self.nodeId not in txn_data[SCHEDULE]:
                logger.info("Node '{}' disregards upgrade txn {}".format(
                    self.nodeName, txn))
                return

            last_event = self.lastActionEventInfo
            if last_event:
                if (last_event.data.upgrade_id == upgrade_id and
                        last_event.ev_type in FINALIZING_EVENT_TYPES):
                    logger.info(
                        "Node '{}' has already performed an upgrade with upgrade_id {}. "
                        "Last recorded event is {}"
                        .format(self.nodeName, upgrade_id, last_event.data))
                    return

            when = txn_data[SCHEDULE][self.nodeId]
            failTimeout = txn_data.get(TIMEOUT, self.defaultActionTimeout)

            if isinstance(when, str):
                when = dateutil.parser.parse(when)

            new_ev_data = UpgradeLogData(when, version, upgrade_id, pkg_name)

            if self.scheduledAction:
                if self.scheduledAction == new_ev_data:
                    logger.debug(
                        "Node {} already scheduled upgrade to version '{}' "
                        .format(self.nodeName, version))
                    return
                else:
                    logger.info(
                        "Node '{}' cancels previous upgrade and schedules a new one to {}"
                        .format(self.nodeName, version))
                    self._cancelScheduledUpgrade(justification)

            logger.info("Node '{}' schedules upgrade to {}".format(self.nodeName, version))

            self._scheduleUpgrade(new_ev_data, failTimeout)
            return

        if action == CANCEL:
            if (self.scheduledAction and
                    self.scheduledAction.version == version):
                self._cancelScheduledUpgrade(justification)
                logger.info("Node '{}' cancels upgrade to {}".format(
                    self.nodeName, version))
            return

        logger.error(
            "Got {} transaction with unsupported action {}".format(
                POOL_UPGRADE, action))

    def _scheduleUpgrade(self,
                         ev_data: UpgradeLogData,
                         failTimeout) -> None:
        """
        Schedules node upgrade to a newer version

        :param ev_data: upgrade event parameters
        """
        logger.info(
            "{}'s upgrader processing upgrade for version {}={}"
            .format(self, ev_data.pkg_name, ev_data.version))
        now = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())

        self._notifier.sendMessageUponNodeUpgradeScheduled(
            "Upgrade of package {} on node '{}' to version {} "
            "has been scheduled on {}"
            .format(ev_data.pkg_name, self.nodeName,
                    ev_data.version, ev_data.when))
        self._actionLog.append_scheduled(ev_data)

        callAgent = partial(self._callUpgradeAgent, ev_data, failTimeout)
        delay = 0
        if now < ev_data.when:
            delay = (ev_data.when - now).total_seconds()
        self.scheduledAction = ev_data
        self._schedule(callAgent, delay)

    def _cancelScheduledUpgrade(self, justification=None) -> None:
        """
        Cancels scheduled upgrade

        :param when: time upgrade was scheduled to
        :param version: version upgrade scheduled for
        """

        if self.scheduledAction:
            why_prefix = ": "
            why = justification
            if justification is None:
                why_prefix = ", "
                why = "cancellation reason not specified"

            ev_data = self.scheduledAction
            logger.info("Cancelling upgrade {}"
                        " of node {}"
                        " of package {}"
                        " to version {}"
                        " scheduled on {}"
                        "{}{}"
                        .format(ev_data.upgrade_id,
                                self.nodeName,
                                ev_data.pkg_name,
                                ev_data.version,
                                ev_data.when,
                                why_prefix,
                                why))

            self._unscheduleAction()
            self._actionLog.append_cancelled(ev_data)
            self._notifier.sendMessageUponPoolUpgradeCancel(
                "Upgrade of package {} on node '{}' to version {} "
                "has been cancelled due to {}"
                .format(ev_data.pkg_name, self.nodeName,
                        ev_data.version, why))

    def _callUpgradeAgent(self, ev_data, failTimeout) -> None:
        """
        Callback which is called when upgrade time come.
        Writes upgrade record to upgrade log and asks
        node control service to perform upgrade

        :param when: upgrade time
        :param version: version to upgrade to
        """

        logger.info("{}'s upgrader calling agent for upgrade".format(self))
        self._actionLog.append_started(ev_data)
        self._action_start_callback()
        self.scheduledAction = None
        asyncio.ensure_future(
            self._sendUpgradeRequest(ev_data, failTimeout))

    async def _sendUpgradeRequest(self, ev_data, failTimeout):
        retryLimit = self.retry_limit
        while retryLimit:
            try:
                msg = UpgradeMessage(
                    version=ev_data.version.full,
                    pkg_name=ev_data.pkg_name
                ).toJson()
                logger.info("Sending message to control tool: {}".format(msg))
                await self._open_connection_and_send(msg)
                break
            except Exception as ex:
                logger.warning("Failed to communicate to control tool: {}".format(ex))
                asyncio.sleep(self.retry_timeout)
                retryLimit -= 1
        if not retryLimit:
            self._action_failed(
                ev_data,
                reason="problems in communication with node control service")
            self._unscheduleAction()
        else:
            logger.info("Waiting {} minutes for upgrade to be performed".format(failTimeout))
            timesUp = partial(self._declareTimeoutExceeded, ev_data)
            self._schedule(timesUp, self.get_timeout(failTimeout))

    def _declareTimeoutExceeded(self, ev_data: UpgradeLogData):
        """
        This function is called when time for upgrade is up
        """
        logger.info("Timeout exceeded for {}:{}"
                    .format(ev_data.when, ev_data.version))
        last = self._actionLog.last_event
        # TODO test this
        if (last and last.ev_type == UpgradeLog.Events.failed and
                last.data == ev_data):
            return None

        self._action_failed(ev_data, reason="exceeded upgrade timeout")

        self._unscheduleAction()
        self._actionFailedCallback()

    def _action_failed(self,
                       ev_data: UpgradeLogData,
                       reason=None,
                       external_reason=False):
        if reason is None:
            reason = "unknown reason"
        error_message = (
            "Node {} failed upgrade {} to "
            "version {} of package {} "
            "scheduled on {} because of {}"
            .format(self.nodeName,
                    ev_data.upgrade_id,
                    ev_data.version,
                    ev_data.pkg_name,
                    ev_data.when,
                    reason)
        )
        logger.error(error_message)
        if external_reason:
            logger.error("This problem may have external reasons, "
                         "check syslog for more information")
        self._notifier.sendMessageUponNodeUpgradeFail(error_message)

    def isScheduleValid(self, schedule, node_srvs, force) -> (bool, str):
        """
        Validates schedule of planned node upgrades

        :param schedule: dictionary of node ids and upgrade times
        :param node_srvs: dictionary of node ids and services
        :return: a 2-tuple of whether schedule valid or not and the reason
        """

        # flag "force=True" ignore basic checks! only datetime format is
        # checked
        times = []
        non_demoted_nodes = set([k for k, v in node_srvs.items() if v])
        if not force and set(schedule.keys()) != non_demoted_nodes:
            return False, 'Schedule should contain id of all nodes'
        now = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
        for dateStr in schedule.values():
            try:
                when = dateutil.parser.parse(dateStr)
                if when <= now and not force:
                    return False, '{} is less than current time'.format(when)
                times.append(when)
            except ValueError:
                return False, '{} cannot be parsed to a time'.format(dateStr)
        if force:
            return True, ''
        times = sorted(times)
        for i in range(len(times) - 1):
            diff = (times[i + 1] - times[i]).total_seconds()
            if diff < self.config.MinSepBetweenNodeUpgrades:
                return False, 'time span between upgrades is {} ' \
                              'seconds which is less than specified ' \
                              'in the config'.format(diff)
        return True, ''


class UpgradeMessage(NodeControlToolMessage):
    """
    Data structure that represents request for node update
    """

    def __init__(self, version: str, pkg_name: str):
        super().__init__(UPGRADE_MESSAGE)
        self.version = version
        self.pkg_name = pkg_name

    def toJson(self):
        import json
        return json.dumps(self.__dict__)
