import os
from collections import deque
from datetime import datetime
from functools import partial
from typing import Tuple, Union, Optional

import dateutil.parser
import dateutil.tz

from plenum.common.log import getlogger
from plenum.common.txn import NAME, TXN_TYPE
from plenum.common.txn import VERSION
from plenum.server.has_action_queue import HasActionQueue
from sovrin_common.txn import ACTION, POOL_UPGRADE, START, SCHEDULE, CANCEL

logger = getlogger()


class Upgrader(HasActionQueue):
    def __init__(self, nodeId, config, baseDir, ledger):
        self.nodeId = nodeId
        self.config = config
        self.baseDir = baseDir
        self.ledger = ledger

        # TODO: Rename to `upgradedVersion`
        self.hasCodeBeenUpgraded = self._hasCodeBeenUpgraded()
        self.storeCurrentVersion()

        # TODO: Rename to `failedToUpgrade`
        self.didLastUpgradeFail = self._didLastUpgradeFail()

        if self.didLastUpgradeFail:
            # TODO: Call `lastUpgradeFailed` to tell the agent and then agent
            # should remove file
            pass
        else:
            self.removeNextVersionFile()
        self.scheduledUpgrade = None    # type: Tuple[str, int]
        HasActionQueue.__init__(self)

    def service(self):
        return self._serviceActions()

    def processLedger(self):
        # Assumption: Only version is enough to identify a release, no hash
        # checking is done
        currentVer = self.getVersion()
        upgrades = {}   # Map of version to scheduled time
        for txn in self.ledger.getAllTxn().values():
            if txn[TXN_TYPE] == POOL_UPGRADE:
                if txn[ACTION] == START:
                    if self.isVersionHigher(currentVer, txn[VERSION]):
                        if self.nodeId not in txn[SCHEDULE]:
                            logger.warn('{} not present in schedule {}'.
                                        format(self.nodeId, txn[SCHEDULE]))
                        else:
                            upgrades[txn[VERSION]] = txn[SCHEDULE][self.nodeId]
                elif txn[ACTION] == CANCEL:
                    if txn[VERSION] not in upgrades:
                        logger.warn('{} encountered before {}'.
                                    format(CANCEL, START))
                    else:
                        upgrades.pop(txn[VERSION])
                else:
                    logger.error('{} cannot be {}'.format(ACTION, txn[ACTION]))

        upgrades = sorted(upgrades.items(),
                          key=lambda x: self.getNumericValueOfVersion(x[0]),
                          reverse=True)
        if upgrades:
            latestVer, upgradeAt = upgrades[0]
            self._upgrade(latestVer, upgradeAt)

    @staticmethod
    def getVersion():
        from sovrin_node.__metadata__ import __version__
        return __version__

    @staticmethod
    def getNumericValueOfVersion(version):
        version = list(map(int, version.split('.')))
        return sum([v*(10**i) for i, v in enumerate(version)])

    @staticmethod
    def isVersionHigher(oldVer, newVer):
        assert oldVer.count('.') == newVer.count('.'), 'Cannot compare {} ' \
                                                       'and {}'.format(
            oldVer, newVer)
        oldVerVal = Upgrader.getNumericValueOfVersion(oldVer)
        newVerVal = Upgrader.getNumericValueOfVersion(newVer)
        return newVerVal > oldVerVal

    @property
    def lastVersionFilePath(self):
        return os.path.join(self.baseDir, self.config.lastRunVersionFile)

    @property
    def nextVersionFilePath(self):
        return os.path.join(self.baseDir, self.config.nextVersionFile)

    def storeCurrentVersion(self):
        version = self.getVersion()
        with open(self.lastVersionFilePath, 'w') as f:
            f.write(version)
            f.flush()

    def storeNextVersionToUpgrade(self, version):
        with open(self.nextVersionFilePath, 'w') as f:
            f.write(version)
            f.flush()

    def isCurrentVersionLower(self, version):
        return not self.isVersionHigher(self.getVersion(), version)

    def _hasCodeBeenUpgraded(self) -> Optional[str]:
        if not os.path.isfile(self.lastVersionFilePath):
            # If last version file not found means node starting on a fresh
            # machine
            return None
        else:
            with open(self.lastVersionFilePath, 'r') as f:
                version = f.read()
                if self.isVersionHigher(version, self.getVersion()):
                    return self.getVersion()

    def _didLastUpgradeFail(self) -> Optional[str]:
        if not os.path.isfile(self.nextVersionFilePath):
            # If next version file not found means the file has been processed
            # and deleted
            return None
        else:
            with open(self.nextVersionFilePath, 'r') as f:
                version = f.read()
                if self.isVersionHigher(version, self.getVersion()):
                    return version

    def isScheduleValid(self, schedule, nodeIds):
        times = []
        if set(schedule.keys()) != nodeIds:
            return False, 'Schedule should contain id of all nodes'
        unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
        for dateStr in schedule.values():
            try:
                dt = dateutil.parser.parse(dateStr)
                if dt <= unow:
                    return False, '{} is less than current time'.format(dt)
                times.append(dt)
            except ValueError:
                return False, '{} cannot be parsed to a time'.format(dateStr)

        times = sorted(times)
        for i in range(len(times)):
            if i == len(times) - 1:
                break
            diff = (times[i+1] - times[i]).seconds
            if diff < self.config.MinSepBetweenNodeUpgrades:
                return False, 'time span between upgrades is {} seconds which' \
                              ' is less than {}, specified in the config'.\
                    format(diff, self.config.MinSepBetweenNodeUpgrades)

        return True, ''

    def statusInLedger(self, name, version):
        t = {}
        for txn in self.ledger.getAllTxn().values():
            if txn[NAME] == name and txn[VERSION] == version:
                t = txn
        if not t:
            return None
        else:
            return t[ACTION]

    def handleUpgradeTxn(self, txn):
        if txn[TXN_TYPE] == POOL_UPGRADE:
            if txn[ACTION] == START:
                if self.nodeId not in txn[SCHEDULE]:
                    logger.warn('{} not present in schedule {}'.
                                format(self.nodeId, txn[SCHEDULE]))
                else:
                    if not self.scheduledUpgrade and \
                            self.isVersionHigher(self.getVersion(), txn[VERSION]):
                        # If no upgrade has been scheduled
                        self._upgrade(txn[VERSION], txn[SCHEDULE][self.nodeId])
                    elif self.scheduledUpgrade and self.isVersionHigher(
                            self.scheduledUpgrade[0], txn[VERSION]):
                        # If upgrade has been scheduled but for version lower
                        # than current transaction
                        self.aqStash = deque()
                        self.scheduledUpgrade = None
                        self._upgrade(txn[VERSION], txn[SCHEDULE][self.nodeId])
            elif txn[ACTION] == CANCEL:
                if self.scheduledUpgrade and self.scheduledUpgrade[0] == txn[VERSION]:
                    self.scheduledUpgrade = None
                    self.aqStash = deque()
                    # An efficient way would be to enqueue all upgrades to do
                    # and then for each cancel keep dequeuing them
                    self.processLedger()

    def _upgrade(self, version, when: Union[datetime, str]):
        assert isinstance(when, (str, datetime))
        logger.info(
            "{}'s upgrader processing upgrade for version".
                format(self.nodeId, version))
        if isinstance(when, str):
            when = dateutil.parser.parse(when)
        unow = datetime.utcnow().replace(tzinfo=dateutil.tz.tzutc())
        if when > unow:
            delay = (when - unow).seconds
            self._schedule(partial(self.callUpgradeAgent, version), delay)
            self.scheduledUpgrade = (version, delay)
        else:
            self.callUpgradeAgent(version)
            return True

    def callUpgradeAgent(self, version):
        # TODO: Call upgrade agent
        logger.info("{}'s upgrader calling agent for upgrade".format(self.nodeId))
        self.storeNextVersionToUpgrade(version)
        self.scheduledUpgrade = None

    def lastUpgradeFailed(self):
        # TODO: Tell the agent that upgrade failed
        self.removeNextVersionFile()

    def removeNextVersionFile(self):
        try:
            os.remove(self.nextVersionFilePath)
        except OSError:
            pass

