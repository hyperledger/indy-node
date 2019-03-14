from indy_node.server.action_log import ActionLogData, ActionLogEvents, ActionLog


class RestartLogData(ActionLogData):
    pass


class RestartLog(ActionLog):

    Events = ActionLogEvents

    """
    Append-only event log of restart event
    """
    def __init__(self, file_path):
        super().__init__(
            file_path,
            data_class=RestartLogData,
            event_types=ActionLogEvents,
            delimiter='\t'
        )

    def append_scheduled(self, data: RestartLogData):
        super().append_scheduled(data)

    def append_started(self, data: RestartLogData):
        super().append_started(data)

    def append_succeeded(self, data: RestartLogData):
        super().append_succeeded(data)

    def append_failed(self, data: RestartLogData):
        super().append_failed(data)

    def append_cancelled(self, data: RestartLogData):
        super().append_cancelled(data)
