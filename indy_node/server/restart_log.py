from indy_node.server.action_log import ActionLogData, ActionLogEvents, ActionLog


class RestartLogData(ActionLogData):
    pass


class RestartLog(ActionLog):

    Events = ActionLogEvents

    """
    Append-only event log of restart event
    """
    def __init__(self, *args, **kwargs):
        kwargs.pop('event_types', None)
        super().__init__(*args, event_types=ActionLogEvents, **kwargs)
