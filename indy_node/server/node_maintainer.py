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


class NodeMaintainer(HasActionQueue):
    defaultActionTimeout = 10  # minutes

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
            # append SUCCESS to the action log
            self._update_action_log_for_started_action()

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
