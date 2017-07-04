import os
from collections import deque
from datetime import datetime, timedelta
from functools import cmp_to_key
from functools import partial
from typing import Tuple, Union, Optional

import dateutil.parser
import dateutil.tz

from stp_core.common.log import getlogger
from plenum.common.constants import NAME, TXN_TYPE
from plenum.common.constants import VERSION
from plenum.server.has_action_queue import HasActionQueue
from sovrin_common.constants import ACTION, POOL_UPGRADE, START, SCHEDULE, \
    CANCEL, JUSTIFICATION, TIMEOUT
from sovrin_node.server.upgrade_log import UpgradeLog
from plenum.server import notifier_plugin_manager
import asyncio

logger = getlogger()


class Upgrader(HasActionQueue):

    defaultUpgradeTimeout = 10  # minutes

    @staticmethod
    def getVersion():
        from sovrin_node.__metadata__ import __version__
        return __version__

    @staticmethod
    def isVersionHigher(oldVer, newVer):
        r = Upgrader.compareVersions(oldVer, newVer)
        return True if r == 1 else False

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
    def versionsDescOrder(versions):
        "Returns versions ordered in descending order"
        return sorted(versions,
                      key=cmp_to_key(Upgrader.compareVersions))

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
                 upgradeFailedCallback = None):

        self.nodeId = nodeId
        self.nodeName = nodeName
        self.config = config
        self.dataDir = dataDir
        self.ledger = ledger
        self.scheduledUpgrade = None  # type: Tuple[str, int]
        self._notifier = notifier_plugin_manager.PluginManager()
        self._upgradeLog = upgradeLog if upgradeLog else \
            self.__defaultLog(dataDir, config)
        self._upgradeFailedCallback = \
            upgradeFailedCallback if upgradeFailedCallback else lambda: None

        self.__isItFirstRunAfterUpgrade = None

        if self.isItFirstRunAfterUpgrade:
            (when, version) = self.lastExecutedUpgradeInfo
            if self.didLastExecutedUpgradeSucceeded:
                self._upgradeLog.appendSucceeded(when, version)
                logger.debug("Node '{}' successfully upgraded to version {}"
                             .format(nodeName, version))
                self._notifier.sendMessageUponNodeUpgradeComplete(
                    "Upgrade of node '{}' to version {} scheduled on {} "
                    "completed successfully"
                    .format(nodeName, version, when))
            else:
                self._upgradeLog.appendFailed(when, version)
                logger.error("Failed to upgrade node '{}' to version {}"
                             .format(nodeName, version))
                self._notifier.sendMessageUponNodeUpgradeFail(
                    "Upgrade of node '{}' to version {} "
                    "scheduled on {} failed"
                    .format(nodeName, version, when))
        HasActionQueue.__init__(self)

    def __repr__(self):
        # Since nodeid can be null till pool ledger has not caught up
        return self.nodeId or ''

    def service(self):
        return self._serviceActions()

    @property
    def lastExecutedUpgradeInfo(self) -> Optional[Tuple[str, str]]:
        """
        Version of last performed upgrade

        :returns: bool or None if there were no upgrades
        """
        lastEvent = self._upgradeLog.lastEvent
        return lastEvent[2:4] if lastEvent else None

    def processLedger(self) -> None:
        """
        Checks ledger for planned but not yet performed upgrades
        and schedules upgrade for the most recent one

        Assumption: Only version is enough to identify a release, no hash
        checking is done
        :return:
        """
        logger.info('{} processing config ledger for any upgrades'.format(self),
                    extra={"tags": ["node-config"]})
        currentVer = self.getVersion()
        upgrades = {}  # Map of version to scheduled time
        for _, txn in self.ledger.getAllTxn():
            if txn[TXN_TYPE] == POOL_UPGRADE:
                version = txn[VERSION]
                action = txn[ACTION]
                if action == START and \
                        self.isVersionHigher(currentVer, version):
                    schedule = txn[SCHEDULE]
                    if self.nodeId not in schedule:
                        logger.warning('{} not present in schedule {}'.
                                    format(self, schedule))
                    else:
                        upgrades[version] = schedule[self.nodeId]
                elif action == CANCEL:
                    if version not in upgrades:
                        logger.error('{} encountered before {}'.
                                     format(CANCEL, START))
                    else:
                        upgrades.pop(version)
                else:
                    logger.error('{} cannot be {}'.format(ACTION, action))
        upgradeKeys = self.versionsDescOrder(upgrades.keys())
        if upgradeKeys:
            latestVer, upgradeAt = upgradeKeys[0], upgrades[upgradeKeys[0]]
            logger.info('{} found upgrade for version {} to be run at {}'.
                        format(self, latestVer, upgradeAt))
            self._scheduleUpgrade(latestVer,
                                  upgradeAt,
                                  self.defaultUpgradeTimeout)
            #TODO: Consider reporting a signal if the node is going to upgrade
            # very soon so that catchup for domain ledger does not start

    @property
    def didLastExecutedUpgradeSucceeded(self) -> bool:
        """
        Checks last record in upgrade log to find out whether it
        is about scheduling upgrade. If so - checks whether current version
        is equals or higher than the one in that record

        :returns: upgrade execution result
        """
        lastEvent = self._upgradeLog.lastEvent
        if lastEvent:
            currentVersion = self.getVersion()
            scheduledVersion = lastEvent[3]
            return self.compareVersions(currentVersion, scheduledVersion) <= 0
        return False

    @property
    def isItFirstRunAfterUpgrade(self):
        # TODO: What if node restarts after upgrading but before acknowledging?
        if self.__isItFirstRunAfterUpgrade is None:
            lastEvent = self._upgradeLog.lastEvent
            self.__isItFirstRunAfterUpgrade = lastEvent and \
                                              lastEvent[1] == UpgradeLog.UPGRADE_SCHEDULED
        return self.__isItFirstRunAfterUpgrade

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

    def statusInLedger(self, name, version) -> dict:
        """
        Searches ledger for transaction that schedules or cancels
        upgrade to specified version

        :param name:
        :param version:
        :return: corresponding transaction
        """

        upgradeTxn = {}
        for _, txn in self.ledger.getAllTxn():
            if txn.get(NAME) == name and txn.get(VERSION) == version:
                upgradeTxn = txn
        return upgradeTxn.get(ACTION)

    def handleUpgradeTxn(self, txn) -> None:
        """
        Handles transaction of type POOL_UPGRADE
        Can schedule or cancel upgrade to a newer
        version at specified time

        :param txn:
        """

        if txn[TXN_TYPE] == POOL_UPGRADE:
            action = txn[ACTION]
            version = txn[VERSION]
            justification = txn.get(JUSTIFICATION)
            currentVersion = self.getVersion()

            if action == START:
                #forced txn could have partial schedule list
                if self.nodeId not in txn[SCHEDULE]:
                    return
                when = txn[SCHEDULE][self.nodeId]
                failTimeout = txn.get(TIMEOUT, self.defaultUpgradeTimeout)

                if not self.scheduledUpgrade:
                    if self.isVersionHigher(currentVersion, version):
                        # If no upgrade has been scheduled
                        self._scheduleUpgrade(version, when, failTimeout)
                else:
                    if self.isVersionHigher(self.scheduledUpgrade[0], version):
                        # If upgrade has been scheduled but for version
                        # lower than this transaction propose
                        self._cancelScheduledUpgrade(justification)
                        self._scheduleUpgrade(version, when, failTimeout)

            elif action == CANCEL:
                if self.scheduledUpgrade and \
                                self.scheduledUpgrade[0] == version:
                    self._cancelScheduledUpgrade(justification)
                    self.processLedger()
            else:
                logger.error(
                    "Got {} transaction with unsupported action {}".format(
                        POOL_UPGRADE, action))

    def _scheduleUpgrade(self,
                         version,
                         when: Union[datetime, str],
                         failTimeout) -> None:
        """
        Schedules node upgrade to a newer version

        :param version: version to upgrade to
        :param when: upgrade time
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
        self._upgradeLog.appendScheduled(when, version)

        callAgent = partial(self._callUpgradeAgent, when, version, failTimeout)
        if when > now:
            delay = (when - now).seconds
            self._schedule(callAgent, delay)
            self.scheduledUpgrade = (version, delay)
        else:
            callAgent()

    def _cancelScheduledUpgrade(self, justification=None) -> None:
        """
        Cancels scheduled upgrade

        :param when: time upgrade was scheduled to
        :param version: version upgrade scheduled for
        """

        if self.scheduledUpgrade:
            why = justification if justification else "some reason"
            (version, when) = self.scheduledUpgrade
            logger.debug("Cancelling upgrade of node '{}' "
                         "to version {} due to {}"
                         .format(self.nodeName, version, why))
            self._unscheduleUpgrade()
            self._upgradeLog.appendCancelled(when, version)
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

    def _callUpgradeAgent(self, when, version, failTimeout) -> None:
        """
        Callback which is called when upgrade time come.
        Writes upgrade record to upgrade log and asks
        node control service to perform upgrade

        :param when: upgrade time
        :param version: version to upgrade to
        """

        logger.info("{}'s upgrader calling agent for upgrade".format(self))
        self._upgradeLog.appendScheduled(when, version)
        self.scheduledUpgrade = None
        asyncio.ensure_future(self._sendUpdateRequest(when, version, failTimeout))

    async def _sendUpdateRequest(self, when, version, failTimeout):
        retryLimit = 3
        retryTimeout = 5  # seconds
        while retryLimit:
            try:
                controlServiceHost = self.config.controlServiceHost
                controlServicePort = self.config.controlServicePort
                msg = UpgradeMessage(version=version).toJson()
                msgBytes = bytes(msg, "utf-8")
                _, writer = await asyncio.open_connection(
                    host=controlServiceHost,
                    port=controlServicePort
                )
                writer.write(msgBytes)
                writer.close()
                break
            except Exception as ex:
                logger.debug(
                    "Failed to communicate to control tool: {}".format(ex))
                asyncio.sleep(retryTimeout)
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
            timesUp = partial(self._declareTimeoutExceeded, when, version)
            self._schedule(timesUp, timedelta(minutes=failTimeout).seconds)

    def _declareTimeoutExceeded(self, when, version):
        """
        This function is called when time for upgrade is up
        """

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
