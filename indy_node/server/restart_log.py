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
