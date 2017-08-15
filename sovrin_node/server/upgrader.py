import os
from collections import deque
from datetime import datetime, timedelta
from functools import cmp_to_key, partial
from typing import Tuple, Union, Optional, Callable, Dict

import dateutil.parser
import dateutil.tz

from stp_core.common.log import getlogger
from plenum.common.constants import TXN_TYPE, VERSION, DATA, IDENTIFIER
from plenum.common.types import f
from plenum.server.has_action_queue import HasActionQueue
from sovrin_common.constants import ACTION, POOL_UPGRADE, START, SCHEDULE, \
    CANCEL, JUSTIFICATION, TIMEOUT, REINSTALL, NODE_UPGRADE, IN_PROGRESS, FORCE
from sovrin_node.server.upgrade_log import UpgradeLog
from plenum.server import notifier_plugin_manager
from ledger.util import F
import asyncio

logger = getlogger()


class Upgrader(HasActionQueue):

    defaultUpgradeTimeout = 10  # minutes

    @staticmethod
    def getVersion():
        from sovrin_node.__metadata__ import __version__
        return __version__

    @staticmethod
    def is_version_upgradable(old, new, reinstall: bool = False):
        return reinstall or (Upgrader.compareVersions(old, new) != 0)

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

        self.check_upgrade_succeeded()

        HasActionQueue.__init__(self)

    def __repr__(self):
        # Since nodeid can be null till pool ledger has not caught up
        return self.nodeId or ''

    def service(self):
        return self._serviceActions()

    def check_upgrade_succeeded(self):
        if not self.lastUpgradeEventInfo:
            logger.debug('Node {} has no upgrade events'
                         .format(self.nodeName))
            return

        (event_type, when, version, upgrade_id) = self.lastUpgradeEventInfo

        if event_type != UpgradeLog.UPGRADE_STARTED:
            logger.debug('Upgrade for node {} was not scheduled. Last event is {}:{}:{}:{}'
                         .format(self.nodeName, event_type, when, version, upgrade_id))
            return

        if not self.didLastExecutedUpgradeSucceeded:
            self._upgradeLog.appendFailed(when, version, upgrade_id)
            logger.error("Failed to upgrade node '{}' to version {}"
                         .format(self.nodeName, version))
            self._notifier.sendMessageUponNodeUpgradeFail(
                "Upgrade of node '{}' to version {} "
                "scheduled on {} with upgrade_id {} failed"
                .format(self.nodeName, version, when, upgrade_id))
            return

        self._upgradeLog.appendSucceeded(when, version, upgrade_id)
        logger.debug("Node '{}' successfully upgraded to version {}"
                     .format(self.nodeName, version))
        self._notifier.sendMessageUponNodeUpgradeComplete(
            "Upgrade of node '{}' to version {} scheduled on {} "
            " with upgrade_id {} completed successfully"
            .format(self.nodeName, version, when, upgrade_id))

    def should_notify_about_upgrade_result(self):
        last_node_upgrade_txn = self.get_last_node_upgrade_txn()
        logger.debug("Node's '{}' last upgrade txn is {}"
                     .format(self.nodeName, last_node_upgrade_txn))
        return last_node_upgrade_txn and last_node_upgrade_txn[TXN_TYPE] == NODE_UPGRADE \
               and last_node_upgrade_txn[DATA] and last_node_upgrade_txn[DATA][ACTION] == IN_PROGRESS \
               and self.lastUpgradeEventInfo \
               and (self.lastUpgradeEventInfo[0] == UpgradeLog.UPGRADE_SUCCEEDED
                    or self.lastUpgradeEventInfo[0] == UpgradeLog.UPGRADE_FAILED)

    def get_last_node_upgrade_txn(self, start_no: int = None):
        return self.get_upgrade_txn(lambda txn: txn[TXN_TYPE] == NODE_UPGRADE and txn[IDENTIFIER] == self.nodeId,
                                    start_no=start_no, reverse=True)

    def get_upgrade_txn(self, predicate: Callable = None, start_no: int = None,
                        reverse: bool = False) -> Optional[Dict]:
        def txn_filter(txn):
            return not predicate or predicate(txn)

        def traverse_end_condition(seq_no):
            if reverse:
                return seq_no > 0
            return seq_no < len(self.ledger)

        inc = 1
        init_start_no = 0
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

    #TODO: PoolConfig and Updater both read config ledger independently
    def processLedger(self) -> None:
        """
        Checks ledger for planned but not yet performed upgrades
        and schedules upgrade for the most recent one

        Assumption: Only version is enough to identify a release, no hash
        checking is done
        :return:
        """
        logger.debug('{} processing config ledger for any upgrades'.format(self))
        current_version = self.getVersion()
        last_pool_upgrade_txn_start = self.get_upgrade_txn(
            lambda txn: txn[TXN_TYPE] == POOL_UPGRADE and txn[ACTION] == START, reverse=True)
        if last_pool_upgrade_txn_start:
            logger.debug('{} found upgrade START txn {}'.format(self, last_pool_upgrade_txn_start))
            last_pool_upgrade_txn_seq_no = last_pool_upgrade_txn_start[F.seqNo.name]

            # searching for CANCEL for this upgrade submitted after START txn
            last_pool_upgrade_txn_cancel = self.get_upgrade_txn(
                lambda txn: txn[TXN_TYPE] == POOL_UPGRADE and txn[ACTION] == CANCEL and
                            txn[VERSION] == current_version,
                start_no=last_pool_upgrade_txn_seq_no)
            if last_pool_upgrade_txn_cancel:
                logger.debug('{} found upgrade CANCEL txn {}'.format(self, last_pool_upgrade_txn_cancel))
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

    def isScheduleValid(self, schedule, nodeIds, force) -> (bool, str):
        """
        Validates schedule of planned node upgrades

        :param schedule: dictionary of node ids and upgrade times
        :param nodeIds: real node ids
        :return: whether schedule valid
        """

        # flag "force=True" ignore basic checks! only datetime format is checked
        times = []
        if not force and set(schedule.keys()) != nodeIds:
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
        FINALIZING_EVENT_TYPES = [UpgradeLog.UPGRADE_SUCCEEDED, UpgradeLog.UPGRADE_FAILED]

        if txn[TXN_TYPE] == POOL_UPGRADE:
            logger.debug("Node '{}' handles upgrade txn {}".format(self.nodeName, txn))
            action = txn[ACTION]
            version = txn[VERSION]
            justification = txn.get(JUSTIFICATION)
            reinstall = txn.get(REINSTALL, False)
            currentVersion = self.getVersion()
            upgrade_id = self.get_upgrade_id(txn)

            if action == START:
                #forced txn could have partial schedule list
                if self.nodeId not in txn[SCHEDULE]:
                    logger.debug("Node '{}' disregards upgrade txn {}".format(self.nodeName, txn))
                    return

                last_event = self.lastUpgradeEventInfo
                if last_event and last_event[3] == upgrade_id and last_event[0] in FINALIZING_EVENT_TYPES:
                    logger.debug("Node '{}' has already performed an upgrade with upgrade_id {}. "
                                 "Last recorded event is {}".
                                 format(self.nodeName, upgrade_id, last_event))
                    return

                when = txn[SCHEDULE][self.nodeId]
                failTimeout = txn.get(TIMEOUT, self.defaultUpgradeTimeout)

                if self.is_version_upgradable(currentVersion, version, reinstall):
                    logger.info("Node '{}' schedules upgrade to {}".format(self.nodeName, version))

                    if self.scheduledUpgrade:
                        logger.info("Node '{}' cancels previous upgrade and schedules a new one to {}".
                                    format(self.nodeName, version))
                        self._cancelScheduledUpgrade(justification)

                    self._scheduleUpgrade(version, when, failTimeout, upgrade_id)
                return

            if action == CANCEL:
                if self.scheduledUpgrade and \
                                self.scheduledUpgrade[0] == version:
                    self._cancelScheduledUpgrade(justification)
                    logger.debug("Node '{}' cancels upgrade to {}".format(self.nodeName, version))
                return

            logger.error("Got {} transaction with unsupported action {}".format(POOL_UPGRADE, action))

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
            "Upgrade of node '{}' to version {} has been scheduled on {}"
            .format(self.nodeName, version, when))
        self._upgradeLog.appendScheduled(when, version, upgrade_id)

        callAgent = partial(self._callUpgradeAgent, when, version, failTimeout, upgrade_id)
        delay = 0
        if now < when:
            delay = (when - now).seconds
        self.scheduledUpgrade = (version, delay, upgrade_id)
        self._schedule(callAgent, delay)

    def _cancelScheduledUpgrade(self, justification=None) -> None:
        """
        Cancels scheduled upgrade

        :param when: time upgrade was scheduled to
        :param version: version upgrade scheduled for
        """

        if self.scheduledUpgrade:
            why = justification if justification else "some reason"
            (version, when, upgrade_id) = self.scheduledUpgrade
            logger.debug("Cancelling upgrade of node '{}' "
                         "to version {} due to {}"
                         .format(self.nodeName, version, why))
            self._unscheduleUpgrade()
            self._upgradeLog.appendCancelled(when, version, upgrade_id)
            self._notifier.sendMessageUponPoolUpgradeCancel(
                "Upgrade of node '{}' to version {} "
                "has been cancelled due to {}"
                .format(self.nodeName, version, why))

    def _unscheduleUpgrade(self):
        """
        Unschedule current upgrade

        Note that it does not add record to upgrade log and does not do
        required steps to resume previous upgrade. If you need this - use
        _cancelScheduledUpgrade

        """
        self.aqStash = deque()
        self.scheduledUpgrade = None

    def _callUpgradeAgent(self, when, version, failTimeout, upgrade_id) -> None:
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
        asyncio.ensure_future(self._sendUpdateRequest(when, version, failTimeout))

    async def _sendUpdateRequest(self, when, version, failTimeout):
        retryLimit = self.retry_limit
        while retryLimit:
            try:
                msg = UpgradeMessage(version=version).toJson()
                logger.debug("Sending message to control tool: {}".format(msg))
                await self._open_connection_and_send(msg)
                break
            except Exception as ex:
                logger.debug("Failed to communicate to control tool: {}".format(ex))
                asyncio.sleep(self.retry_timeout)
                retryLimit -= 1
        if not retryLimit:
            logger.error("Failed to send update request!")
            self._notifier.sendMessageUponNodeUpgradeFail(
                "Upgrade of node '{}' to version {} failed "
                "because of problems in communication with "
                "node control service"
                .format(self.nodeName, version))
            self._unscheduleUpgrade()
            self._upgradeFailedCallback()
        else:
            logger.debug("Waiting {} minutes for upgrade to be performed".format(failTimeout))
            timesUp = partial(self._declareTimeoutExceeded, when, version)
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

    def _declareTimeoutExceeded(self, when, version):
        """
        This function is called when time for upgrade is up
        """

        logger.debug("Timeout exceeded for {}:{}".format(when, version))
        last = self._upgradeLog.lastEvent
        if last and last[1:-1] == (UpgradeLog.UPGRADE_FAILED, when, version):
            return None

        logger.error("Upgrade to version {} scheduled on {} "
                     "failed because timeout exceeded")
        self._notifier.sendMessageUponNodeUpgradeFail(
            "Upgrade of node '{}' to version {} failed "
            "because if exceeded timeout"
            .format(self.nodeName, version))
        self._unscheduleUpgrade()
        self._upgradeFailedCallback()


class UpgradeMessage:
    """
    Data structure that represents request for node update
    """

    def __init__(self, version: str):
        self.version = version

    def toJson(self):
        import json
        return json.dumps(self.__dict__)
