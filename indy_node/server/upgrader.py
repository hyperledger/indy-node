import os
from collections import deque
from datetime import datetime, timedelta
from functools import partial
from typing import Tuple, Union, Optional, Callable, Dict

import dateutil.parser
import dateutil.tz

from stp_core.common.log import getlogger
from plenum.common.constants import TXN_TYPE, VERSION, DATA, IDENTIFIER
from plenum.common.types import f
from plenum.server.has_action_queue import HasActionQueue
from indy_common.constants import ACTION, POOL_UPGRADE, START, SCHEDULE, \
    CANCEL, JUSTIFICATION, TIMEOUT, REINSTALL, NODE_UPGRADE, IN_PROGRESS, FORCE
from indy_node.server.upgrade_log import UpgradeLog
from plenum.server import notifier_plugin_manager
from ledger.util import F
import asyncio

logger = getlogger()


class Upgrader(HasActionQueue):
    defaultUpgradeTimeout = 10  # minutes

    @staticmethod
    def getVersion():
        from indy_node.__metadata__ import __version__
        return __version__

    @staticmethod
    def is_version_upgradable(old, new, reinstall: bool = False):
        return (Upgrader.compareVersions(old, new) > 0) \
            or (Upgrader.compareVersions(old, new) == 0) and reinstall

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

    @staticmethod
    def get_upgrade_id(txn):
        seq_no = txn.get(F.seqNo.name, '')
        if txn.get(FORCE, None):
            seq_no = ''
        return '{}{}'.format(txn[f.REQ_ID.nm], seq_no)

    @staticmethod
    def get_timeout(timeout):
        return timedelta(minutes=timeout).seconds

    def __defaultLog(self, dataDir, config):
        log = os.path.join(dataDir, config.upgradeLogFile)
        return UpgradeLog(filePath=log)

    def __init__(self,
                 nodeId,
                 nodeName,
                 dataDir,
                 config,
                 ledger,
                 upgradeLog: UpgradeLog = None,
                 upgradeFailedCallback: Callable = None,
                 upgrade_start_callback: Callable = None):

        self.nodeId = nodeId
        self.nodeName = nodeName
        self.config = config
        self.dataDir = dataDir
        self.ledger = ledger
        self.scheduledUpgrade = None  # type: Tuple[str, int, str]
        self._notifier = notifier_plugin_manager.PluginManager()
        self._upgradeLog = upgradeLog if upgradeLog else \
            self.__defaultLog(dataDir, config)
        self._upgradeFailedCallback = \
            upgradeFailedCallback if upgradeFailedCallback else lambda: None
        self._upgrade_start_callback = \
            upgrade_start_callback if upgrade_start_callback else lambda: None

        self.retry_timeout = 5
        self.retry_limit = 3

        self.process_upgrade_log_for_first_run()

        HasActionQueue.__init__(self)

    def __repr__(self):
        # Since nodeid can be null till pool ledger has not caught up
        return self.nodeId or ''

    def service(self):
        return self._serviceActions()

    def process_upgrade_log_for_first_run(self):
        # whether upgrade was started before the Node restarted,
        # that is whether Upgrade Log contains STARTED event
        self._upgrade_started = self._is_upgrade_started()
        if self._upgrade_started:
            # append SUCCESS or FAIL to the Upgrade Log
            self._update_upgrade_log_for_started_upgrade()

    def _is_upgrade_started(self):
        if not self.lastUpgradeEventInfo:
            logger.debug('Node {} has no upgrade events'
                         .format(self.nodeName))
            return False

        (event_type, when, version, upgrade_id) = self.lastUpgradeEventInfo

        if event_type != UpgradeLog.UPGRADE_STARTED:
            logger.debug(
                'Upgrade for node {} was not scheduled. Last event is {}:{}:{}:{}'.format(
                    self.nodeName, event_type, when, version, upgrade_id))
            return False

        return True

    def _update_upgrade_log_for_started_upgrade(self):
        (event_type, when, version, upgrade_id) = self.lastUpgradeEventInfo

        if not self.didLastExecutedUpgradeSucceeded:
            self._upgradeLog.appendFailed(when, version, upgrade_id)
            self._upgrade_failed(version=version,
                                 scheduled_on=when,
                                 upgrade_id=upgrade_id,
                                 external_reason=True)
            return

        self._upgradeLog.appendSucceeded(when, version, upgrade_id)
        logger.info("Node '{}' successfully upgraded to version {}"
                    .format(self.nodeName, version))
        self._notifier.sendMessageUponNodeUpgradeComplete(
            "Upgrade of node '{}' to version {} scheduled on {} "
            " with upgrade_id {} completed successfully"
            .format(self.nodeName, version, when, upgrade_id))

    def should_notify_about_upgrade_result(self):
        # do not rely on NODE_UPGRADE txn in config ledger, since in some cases (for example, when
        # we run POOL_UPGRADE with force=true), we may not have IN_PROGRESS NODE_UPGRADE in the ledger.

        # send NODE_UPGRADE txn only if we were in Upgrade Started state at the very beginning (after Node restarted)
        return self._upgrade_started

    def notified_about_upgrade_result(self):
        self._upgrade_started = False

    def get_last_node_upgrade_txn(self, start_no: int = None):
        return self.get_upgrade_txn(
            lambda txn: txn[TXN_TYPE] == NODE_UPGRADE and txn[IDENTIFIER] == self.nodeId,
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

    @property
    def lastUpgradeEventInfo(self) -> Optional[Tuple[str, str, str, str]]:
        """
        (event, when, version, upgrade_id) of last performed upgrade

        :returns: (event, when, version, upgrade_id) or None if there were no upgrades
        """
        last_event = self._upgradeLog.lastEvent
        return last_event[1:] if last_event else None

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
            lambda txn: txn[TXN_TYPE] == POOL_UPGRADE and txn[ACTION] == START, reverse=True)
        if last_pool_upgrade_txn_start:
            logger.info('{} found upgrade START txn {}'.format(
                self, last_pool_upgrade_txn_start))
            last_pool_upgrade_txn_seq_no = last_pool_upgrade_txn_start[F.seqNo.name]

            # searching for CANCEL for this upgrade submitted after START txn
            last_pool_upgrade_txn_cancel = self.get_upgrade_txn(
                lambda txn:
                txn[TXN_TYPE] == POOL_UPGRADE and txn[ACTION] == CANCEL and
                txn[VERSION] == last_pool_upgrade_txn_start[VERSION],
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
        lastEventInfo = self.lastUpgradeEventInfo
        if lastEventInfo:
            currentVersion = self.getVersion()
            scheduledVersion = lastEventInfo[2]
            return self.compareVersions(currentVersion, scheduledVersion) == 0
        return False

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

    def handleUpgradeTxn(self, txn) -> None:
        """
        Handles transaction of type POOL_UPGRADE
        Can schedule or cancel upgrade to a newer
        version at specified time

        :param txn:
        """
        FINALIZING_EVENT_TYPES = [
            UpgradeLog.UPGRADE_SUCCEEDED, UpgradeLog.UPGRADE_FAILED]

        if txn[TXN_TYPE] != POOL_UPGRADE:
            return

        logger.info("Node '{}' handles upgrade txn {}".format(
            self.nodeName, txn))
        action = txn[ACTION]
        version = txn[VERSION]
        justification = txn.get(JUSTIFICATION)
        reinstall = txn.get(REINSTALL, False)
        currentVersion = self.getVersion()
        upgrade_id = self.get_upgrade_id(txn)

        if action == START:
            # forced txn could have partial schedule list
            if self.nodeId not in txn[SCHEDULE]:
                logger.info("Node '{}' disregards upgrade txn {}".format(
                    self.nodeName, txn))
                return

            last_event = self.lastUpgradeEventInfo
            if last_event and last_event[3] == upgrade_id and last_event[0] in FINALIZING_EVENT_TYPES:
                logger.info(
                    "Node '{}' has already performed an upgrade with upgrade_id {}. "
                    "Last recorded event is {}".format(
                        self.nodeName, upgrade_id, last_event))
                return

            when = txn[SCHEDULE][self.nodeId]
            failTimeout = txn.get(TIMEOUT, self.defaultUpgradeTimeout)

            if not self.is_version_upgradable(
                    currentVersion, version, reinstall):
                return

            if self.scheduledUpgrade:
                if isinstance(when, str):
                    when = dateutil.parser.parse(when)
                if self.scheduledUpgrade == (version, when, upgrade_id):
                    logger.debug("Node {} already scheduled upgrade to version '{}' ".format(
                        self.nodeName, version))
                    return
                else:
                    logger.info(
                        "Node '{}' cancels previous upgrade and schedules a new one to {}".format(
                            self.nodeName, version))
                    self._cancelScheduledUpgrade(justification)

            logger.info("Node '{}' schedules upgrade to {}".format(
                self.nodeName, version))

            self._scheduleUpgrade(
                version, when, failTimeout, upgrade_id)
            return

        if action == CANCEL:
            if self.scheduledUpgrade and self.scheduledUpgrade[0] == version:
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
                         upgrade_id) -> None:
        """
        Schedules node upgrade to a newer version

        :param version: version to upgrade to
        :param when: upgrade time
        :param upgrade_id: upgrade identifier (req_id+seq_no) of a txn that started the upgrade
        """
        assert isinstance(when, (str, datetime))
        logger.info("{}'s upgrader processing upgrade for version {}"
                    .format(self, version))
        if isinstance(when, str):
            when = dateutil.parser.parse(when)
        now = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())

        self._notifier.sendMessageUponNodeUpgradeScheduled(
            "Upgrade of node '{}' to version {} has been scheduled on {}".format(
                self.nodeName, version, when))
        self._upgradeLog.appendScheduled(when, version, upgrade_id)

        callAgent = partial(self._callUpgradeAgent, when,
                            version, failTimeout, upgrade_id)
        delay = 0
        if now < when:
            delay = (when - now).total_seconds()
        self.scheduledUpgrade = (version, when, upgrade_id)
        self._schedule(callAgent, delay)

    def _cancelScheduledUpgrade(self, justification=None) -> None:
        """
        Cancels scheduled upgrade

        :param when: time upgrade was scheduled to
        :param version: version upgrade scheduled for
        """

        if self.scheduledUpgrade:
            why_prefix = ": "
            why = justification
            if justification is None:
                why_prefix = ", "
                why = "cancellation reason not specified"

            (version, when, upgrade_id) = self.scheduledUpgrade
            logger.info("Cancelling upgrade {upgrade_id}"
                        " of node {node}"
                        " to version {version}"
                        " scheduled on {when}"
                        "{why_prefix}{why}"
                        .format(upgrade_id=upgrade_id,
                                node=self.nodeName,
                                version=version,
                                when=when,
                                why_prefix=why_prefix,
                                why=why))

            self._unscheduleUpgrade()
            self._upgradeLog.appendCancelled(when, version, upgrade_id)
            self._notifier.sendMessageUponPoolUpgradeCancel(
                "Upgrade of node '{}' to version {} "
                "has been cancelled due to {}".format(
                    self.nodeName, version, why))

    def _unscheduleUpgrade(self):
        """
        Unschedule current upgrade

        Note that it does not add record to upgrade log and does not do
        required steps to resume previous upgrade. If you need this - use
        _cancelScheduledUpgrade

        """
        self.aqStash = deque()
        self.scheduledUpgrade = None

    def _callUpgradeAgent(self, when, version, failTimeout,
                          upgrade_id) -> None:
        """
        Callback which is called when upgrade time come.
        Writes upgrade record to upgrade log and asks
        node control service to perform upgrade

        :param when: upgrade time
        :param version: version to upgrade to
        """

        logger.info("{}'s upgrader calling agent for upgrade".format(self))
        self._upgradeLog.appendStarted(when, version, upgrade_id)
        self._upgrade_start_callback()
        self.scheduledUpgrade = None
        asyncio.ensure_future(
            self._sendUpdateRequest(when, version, upgrade_id, failTimeout))

    async def _sendUpdateRequest(self, when, version, upgrade_id, failTimeout):
        retryLimit = self.retry_limit
        while retryLimit:
            try:
                msg = UpgradeMessage(version=version).toJson()
                logger.info("Sending message to control tool: {}".format(msg))
                await self._open_connection_and_send(msg)
                break
            except Exception as ex:
                logger.warning("Failed to communicate to control tool: {}"
                               .format(ex))
                asyncio.sleep(self.retry_timeout)
                retryLimit -= 1
        if not retryLimit:
            self._upgrade_failed(version=version,
                                 scheduled_on=when,
                                 upgrade_id=upgrade_id,
                                 reason="problems in communication with "
                                        "node control service")
            self._unscheduleUpgrade()
            self._upgradeFailedCallback()
        else:
            logger.info("Waiting {} minutes for upgrade to be performed"
                        .format(failTimeout))
            timesUp = partial(self._declareTimeoutExceeded, when, version, upgrade_id)
            self._schedule(timesUp, self.get_timeout(failTimeout))

    async def _open_connection_and_send(self, message: str):
        controlServiceHost = self.config.controlServiceHost
        controlServicePort = self.config.controlServicePort
        msgBytes = bytes(message, "utf-8")
        _, writer = await asyncio.open_connection(
            host=controlServiceHost,
            port=controlServicePort
        )
        writer.write(msgBytes)
        writer.close()

    def _declareTimeoutExceeded(self, when, version, upgrade_id):
        """
        This function is called when time for upgrade is up
        """

        logger.info("Timeout exceeded for {}:{}".format(when, version))
        last = self._upgradeLog.lastEvent
        if last and last[1:-1] == (UpgradeLog.UPGRADE_FAILED, when, version):
            return None

        self._upgrade_failed(version=version,
                             scheduled_on=when,
                             upgrade_id=upgrade_id,
                             reason="exceeded upgrade timeout")

        self._unscheduleUpgrade()
        self._upgradeFailedCallback()

    def _upgrade_failed(self, *,
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


class UpgradeMessage:
    """
    Data structure that represents request for node update
    """

    def __init__(self, version: str):
        self.version = version

    def toJson(self):
        import json
        return json.dumps(self.__dict__)
