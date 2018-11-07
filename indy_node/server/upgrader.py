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
from indy_common.constants import ACTION, POOL_UPGRADE, START, SCHEDULE, \
    CANCEL, JUSTIFICATION, TIMEOUT, REINSTALL, NODE_UPGRADE, \
    UPGRADE_MESSAGE, PACKAGE, APP_NAME
from indy_node.server.upgrade_log import UpgradeLog
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
    def getVersion(pkg: str = None):
        if pkg and pkg != APP_NAME:
            ver, _ = NodeControlUtil.curr_pkt_info(pkg)
            return ver

        from indy_node.__metadata__ import __version__
        return __version__

    @staticmethod
    def is_version_upgradable(old, new, reinstall: bool = False):
        return (Upgrader.compareVersions(old, new) > 0) \
            or (Upgrader.compareVersions(old, new) == 0) and reinstall

    @staticmethod
    def get_action_id(txn):
        seq_no = get_seq_no(txn) or ''
        if is_forced(txn):
            seq_no = ''
        return '{}{}'.format(get_req_id(txn), seq_no)

    @staticmethod
    def compareVersions(verA: str, verB: str) -> int:
        if verA == verB:
            return 0

        def parse(x):
            if x.endswith(".0"):
                x = x[:-2]
            return [int(num) for num in x.split(".")]

        partsA = parse(verA)
        partsB = parse(verB)
        for a, b in zip(partsA, partsB):
            if a > b:
                return -1
            if b > a:
                return 1
        lenA = len(list(partsA))
        lenB = len(list(partsB))
        if lenA > lenB:
            return -1
        if lenB > lenA:
            return 1
        return 0

    def _defaultLog(self, dataDir, config):
        log = os.path.join(dataDir, config.upgradeLogFile)
        return UpgradeLog(filePath=log)

    def _is_action_started(self):
        if not self.lastActionEventInfo:
            logger.debug('Node {} has no upgrade events'.format(self.nodeName))
            return False

        (event_type, when, version, upgrade_id, pkg_name) = self.lastActionEventInfo

        if event_type != UpgradeLog.STARTED:
            logger.debug(
                'Upgrade for node {} was not scheduled. Last event is {}:{}:{}:{}:{}'.format(
                    self.nodeName, event_type, when, version, upgrade_id, pkg_name))
            return False

        return True

    def _update_action_log_for_started_action(self):
        (event_type, when, version, upgrade_id, pkg_name) = self.lastActionEventInfo
        self._should_notify_about_upgrade = True
        if not self.didLastExecutedUpgradeSucceeded:
            self._actionLog.appendFailed(when, version, upgrade_id, pkg_name)
            self._action_failed(version=version,
                                scheduled_on=when,
                                upgrade_id=upgrade_id,
                                external_reason=True)
            return

        self._actionLog.appendSucceeded(when, version, upgrade_id, pkg_name)
        logger.info("Node '{}' successfully upgraded to version {}".format(self.nodeName, version))
        self._notifier.sendMessageUponNodeUpgradeComplete(
            "Upgrade of packet {} on node '{}' to version {} scheduled on {} "
            " with upgrade_id {} completed successfully"
            .format(pkg_name, self.nodeName, version, when, upgrade_id))

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
            currentVersion = self.getVersion(lastEventInfo[4])
            scheduledVersion = lastEventInfo[2]
            return self.compareVersions(currentVersion, scheduledVersion) == 0
        return False

    def handleUpgradeTxn(self, txn) -> None:
        """
        Handles transaction of type POOL_UPGRADE
        Can schedule or cancel upgrade to a newer
        version at specified time

        :param txn:
        """
        FINALIZING_EVENT_TYPES = [UpgradeLog.SUCCEEDED, UpgradeLog.FAILED]

        if get_type(txn) != POOL_UPGRADE:
            return

        logger.info("Node '{}' handles upgrade txn {}".format(self.nodeName, txn))
        txn_data = get_payload_data(txn)
        action = txn_data[ACTION]
        version = txn_data[VERSION]
        justification = txn_data.get(JUSTIFICATION)
        pkg_name = txn_data.get(PACKAGE, self.config.UPGRADE_ENTRY)
        upgrade_id = self.get_action_id(txn)

        if action == START:
            # forced txn could have partial schedule list
            if self.nodeId not in txn_data[SCHEDULE]:
                logger.info("Node '{}' disregards upgrade txn {}".format(
                    self.nodeName, txn))
                return

            last_event = self.lastActionEventInfo
            if last_event and last_event[3] == upgrade_id and last_event[0] in FINALIZING_EVENT_TYPES:
                logger.info(
                    "Node '{}' has already performed an upgrade with upgrade_id {}. "
                    "Last recorded event is {}".format(
                        self.nodeName, upgrade_id, last_event))
                return

            when = txn_data[SCHEDULE][self.nodeId]
            failTimeout = txn_data.get(TIMEOUT, self.defaultActionTimeout)

            if self.scheduledAction:
                if isinstance(when, str):
                    when = dateutil.parser.parse(when)
                if self.scheduledAction == (version, when, upgrade_id, pkg_name):
                    logger.debug("Node {} already scheduled upgrade to version '{}' ".format(
                        self.nodeName, version))
                    return
                else:
                    logger.info(
                        "Node '{}' cancels previous upgrade and schedules a new one to {}".format(
                            self.nodeName, version))
                    self._cancelScheduledUpgrade(justification)

            logger.info("Node '{}' schedules upgrade to {}".format(self.nodeName, version))

            self._scheduleUpgrade(version, when, failTimeout, upgrade_id, pkg_name)
            return

        if action == CANCEL:
            if self.scheduledAction and self.scheduledAction[0] == version:
                self._cancelScheduledUpgrade(justification)
                logger.info("Node '{}' cancels upgrade to {}".format(
                    self.nodeName, version))
            return

        logger.error(
            "Got {} transaction with unsupported action {}".format(
                POOL_UPGRADE, action))

    def _scheduleUpgrade(self,
                         version,
                         when: Union[datetime, str],
                         failTimeout,
                         upgrade_id,
                         pkg_name) -> None:
        """
        Schedules node upgrade to a newer version

        :param version: version to upgrade to
        :param when: upgrade time
        :param upgrade_id: upgrade identifier (req_id+seq_no) of a txn that started the upgrade
        :param pkg_name: packet to be upgraded
        """
        assert isinstance(when, (str, datetime))
        logger.info("{}'s upgrader processing upgrade for version {}={}".format(self, pkg_name, version))
        if isinstance(when, str):
            when = dateutil.parser.parse(when)
        now = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())

        self._notifier.sendMessageUponNodeUpgradeScheduled(
            "Upgrade of packet {} on node '{}' to version {} has been scheduled on {}".format(
                pkg_name, self.nodeName, version, when))
        self._actionLog.appendScheduled(when, version, upgrade_id, pkg_name)

        callAgent = partial(self._callUpgradeAgent, when, version, failTimeout, upgrade_id, pkg_name)
        delay = 0
        if now < when:
            delay = (when - now).total_seconds()
        self.scheduledAction = (version, when, upgrade_id, pkg_name)
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

            (version, when, upgrade_id, pkg_name) = self.scheduledAction
            logger.info("Cancelling upgrade {upgrade_id}"
                        " of node {node}"
                        " of packet {packet}"
                        " to version {version}"
                        " scheduled on {when}"
                        "{why_prefix}{why}"
                        .format(upgrade_id=upgrade_id,
                                node=self.nodeName,
                                packet=pkg_name,
                                version=version,
                                when=when,
                                why_prefix=why_prefix,
                                why=why))

            self._unscheduleAction()
            self._actionLog.appendCancelled(when, version, upgrade_id, pkg_name)
            self._notifier.sendMessageUponPoolUpgradeCancel(
                "Upgrade of packet {} on node '{}' to version {} "
                "has been cancelled due to {}".format(pkg_name, self.nodeName, version, why))

    def _callUpgradeAgent(self, when, version, failTimeout, upgrade_id, pkg_name) -> None:
        """
        Callback which is called when upgrade time come.
        Writes upgrade record to upgrade log and asks
        node control service to perform upgrade

        :param when: upgrade time
        :param version: version to upgrade to
        """

        logger.info("{}'s upgrader calling agent for upgrade".format(self))
        self._actionLog.appendStarted(when, version, upgrade_id, pkg_name)
        self._action_start_callback()
        self.scheduledAction = None
        asyncio.ensure_future(
            self._sendUpgradeRequest(when, version, upgrade_id, failTimeout, pkg_name))

    async def _sendUpgradeRequest(self, when, version, upgrade_id, failTimeout, pkg_name):
        retryLimit = self.retry_limit
        while retryLimit:
            try:
                msg = UpgradeMessage(version=version, pkg_name=pkg_name).toJson()
                logger.info("Sending message to control tool: {}".format(msg))
                await self._open_connection_and_send(msg)
                break
            except Exception as ex:
                logger.warning("Failed to communicate to control tool: {}".format(ex))
                asyncio.sleep(self.retry_timeout)
                retryLimit -= 1
        if not retryLimit:
            self._action_failed(version=version,
                                scheduled_on=when,
                                upgrade_id=upgrade_id,
                                reason="problems in communication with node control service")
            self._unscheduleAction()
            self._actionFailedCallback()
        else:
            logger.info("Waiting {} minutes for upgrade to be performed".format(failTimeout))
            timesUp = partial(self._declareTimeoutExceeded, when, version, upgrade_id)
            self._schedule(timesUp, self.get_timeout(failTimeout))

    def _declareTimeoutExceeded(self, when, version, upgrade_id):
        """
        This function is called when time for upgrade is up
        """

        logger.info("Timeout exceeded for {}:{}".format(when, version))
        last = self._actionLog.lastEvent
        if last and last[1:-1] == (UpgradeLog.FAILED, when, version):
            return None

        self._action_failed(version=version,
                            scheduled_on=when,
                            upgrade_id=upgrade_id,
                            reason="exceeded upgrade timeout")

        self._unscheduleAction()
        self._actionFailedCallback()

    def _action_failed(self, *,
                       version,
                       scheduled_on,
                       upgrade_id,
                       reason=None,
                       external_reason=False):
        if reason is None:
            reason = "unknown reason"
        error_message = "Node {node} failed upgrade {upgrade_id} to " \
                        "version {version} scheduled on {scheduled_on} " \
                        "because of {reason}" \
            .format(node=self.nodeName,
                    upgrade_id=upgrade_id,
                    version=version,
                    scheduled_on=scheduled_on,
                    reason=reason)
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
            diff = (times[i + 1] - times[i]).seconds
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
