from abc import ABCMeta, abstractmethod
from collections import deque
from datetime import datetime, timedelta
from typing import Tuple, Callable

from stp_core.common.log import getlogger
from plenum.server.has_action_queue import HasActionQueue
from plenum.server import notifier_plugin_manager
import asyncio

logger = getlogger()


class NodeMaintainer(HasActionQueue, metaclass=ABCMeta):
    defaultActionTimeout = 10  # minutes

    @staticmethod
    def get_timeout(timeout):
        return timedelta(minutes=timeout).seconds

    def __init__(self,
                 nodeId,
                 nodeName,
                 dataDir,
                 config,
                 ledger=None,
                 actionLog=None,
                 actionFailedCallback: Callable = None,
                 action_start_callback: Callable = None):

        self.nodeId = nodeId
        self.nodeName = nodeName
        self.config = config
        self.dataDir = dataDir
        self.ledger = ledger
        self.scheduledAction = None
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
        # whether action was started before the Node restarted,
        # that is whether Action Log contains STARTED event
        if self._is_action_started():
            # append SUCCESS to the action log
            self._update_action_log_for_started_action()

    @property
    def lastActionEventInfo(self):
        """
        action parameters of last performed action

        :returns: action parameters or None if there were no actions
        """
        last_event = self._actionLog.lastEvent
        return last_event[1:] if last_event else None

    def _unscheduleAction(self):
        """
        Unschedule current action

        Note that it does not add record to action log and does not do
        required steps to resume previous action. If you need this - use
        _cancelScheduledAction

        """
        logger.trace("{} unscheduling actions".format(self))
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

    @abstractmethod
    def _defaultLog(self, dataDir, config):
        """
        Default log for store action txns
        :param dataDir:
        :param config:
        :return: ActionLog
        """

    @abstractmethod
    def _update_action_log_for_started_action(self):
        pass

    @abstractmethod
    def _is_action_started(self):
        pass


class NodeControlToolMessage(metaclass=ABCMeta):
    """
    Data structure that represents request for node control tool
    """

    def __init__(self, message_type: str):
        self.message_type = message_type

    def toJson(self):
        import json
        return json.dumps(self.__dict__)
