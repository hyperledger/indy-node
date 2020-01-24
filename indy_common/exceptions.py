class GraphDBNotPresent(Exception):
    reason = 'Install and then configure a Graph Database'


class InvalidConnectionException(Exception):
    pass


class NotFound(RuntimeError):
    pass


class ConnectionNotFound(NotFound):
    def __init__(self, name: str = None):
        if name:
            self.reason = "Connection with name not found".format(name)


class VerkeyNotFound(NotFound):
    pass


class RemoteEndpointNotFound(NotFound):
    pass


class RemotePubkeyNotFound(NotFound):
    pass


class ConnectionAlreadyExists(RuntimeError):
    pass


class LinkNotReady(RuntimeError):
    """
    Some operation is attempted on a link that is not ready for that operation
    """


class NotConnectedToNetwork(RuntimeError):
    pass
