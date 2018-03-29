import abc
import os
from collections import deque
from datetime import datetime, timedelta
from functools import partial
from typing import Tuple, Union, Optional, Callable, Dict

import dateutil.parser
import dateutil.tz

from indy_node.server.restart_log import RestartLog
from stp_core.common.log import getlogger
from plenum.common.constants import TXN_TYPE, VERSION, DATA, IDENTIFIER
from plenum.common.types import f
from plenum.server.has_action_queue import HasActionQueue
from indy_common.constants import ACTION, POOL_UPGRADE, START, SCHEDULE, \
    CANCEL, JUSTIFICATION, TIMEOUT, REINSTALL, NODE_UPGRADE, IN_PROGRESS, FORCE, \
    POOL_RESTART
from plenum.server import notifier_plugin_manager
from ledger.util import F
import asyncio

logger = getlogger()


class NodeController(HasActionQueue):
    defaultActionTimeout = 10  # minutes

    @staticmethod
    def getVersion():
        from indy_node.__metadata__ import __version__
        return __version__

    @staticmethod   
    def get_action_id(txn):
        seq_no = txn.get(F.seqNo.name, '')
        if txn[TXN_TYPE] == POOL_RESTART or txn.get(FORCE, None):
            seq_no = ''
        return '{}{}'.format(txn[f.REQ_ID.nm], seq_no)

    @staticmethod   
    def get_timeout(timeout):
        return timedelta(minutes=timeout).seconds
    

    def __init__(self,
                 nodeId,
                 nodeName,
                 dataDir,
                 config,
                 ledger = None,
                 actionLog = None,
                 actionFailedCallback: Callable = None,
                 action_start_callback: Callable = None):

        self.nodeId = nodeId
        self.nodeName = nodeName
        self.config = config
        self.dataDir = dataDir
        self.ledger = ledger
        self.scheduledAction = None  # type: Tuple[str, int, str]
        self._notifier = notifier_plugin_manager.PluginManager()
        self._actionLog = actionLog if actionLog else \
            self._defaultLog(dataDir, config)
        self._actionFailedCallback = \
            actionFailedCallback if actionFailedCallback else lambda: None
        self._action_start_callback = \
            action_start_callback if action_start_callback else lambda: None

        self.retry_timeout = 5
        self.retry_limit = 3

        self.process_action_log_for_first_run()

        HasActionQueue.__init__(self)

    def __repr__(self):
        # Since nodeid can be null till pool ledger has not caught up
        return self.nodeId or ''

    def service(self):
        return self._serviceActions()

    def process_action_log_for_first_run(self):
        # whether upgrade was started before the Node restarted,
        # that is whether Action Log contains STARTED event
        self._action_started = self._is_action_started()
        if self._action_started:
            # append SUCCESS or FAIL to the Upgrade Log
            self._update_action_log_for_started_action()
            
    def should_notify_about_action_result(self):
        # do not rely on NODE_UPGRADE txn in config ledger, since in some cases (for example, when
        # we run POOL_UPGRADE with force=true), we may not have IN_PROGRESS NODE_UPGRADE in the ledger.

        # send NODE_UPGRADE txn only if we were in Upgrade Started state at the very beginning (after Node restarted)
        return self._action_started

    def notified_about_action_result(self): 
        self._action_started = False
        

    @property 
    def lastActionEventInfo(self) -> Optional[Tuple[str, str, str, str]]:
        """
        (event, when, version, upgrade_id) of last performed upgrade

        :returns: (event, when, version, upgrade_id) or None if there were no upgrades
        """
        last_event = self._actionLog.lastEvent
        return last_event[1:] if last_event else None
    

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
    

    def _unscheduleAction(self): 
        """
        Unschedule current upgrade

        Note that it does not add record to upgrade log and does not do
        required steps to resume previous upgrade. If you need this - use
        _cancelScheduledUpgrade

        """
        self.aqStash = deque()
        self.scheduledAction = None

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

    def _defaultLog(self, dataDir, config):
        """
        Default log for store action txns
        :param dataDir:
        :param config:
        :return: UpgradeLog or ResartLog
        """

    def _update_action_log_for_started_action(self):
        pass

    def _is_action_started(self):
        pass
