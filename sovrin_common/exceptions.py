class GraphDBNotPresent(Exception):
    reason = 'Install and then configure a Graph Database'


class InvalidLinkException(Exception):
    pass


class NotFound(RuntimeError):
    pass


class LinkNotFound(NotFound):
    def __init__(self, name: str=None):
        if name:
            self.reason = "Link with name not found".format(name)


class VerkeyNotFound(NotFound):
    pass


class SchemaNotFound(NotFound):
    pass


class RemoteEndpointNotFound(NotFound):
    pass


class RemotePubkeyNotFound(NotFound):
    pass


class LinkAlreadyExists(RuntimeError):
    pass


class LinkNotReady(RuntimeError):
    """
    Some operation is attempted on a link that is not ready for that operation
    """
    pass


class NotConnectedToNetwork(RuntimeError):
    pass
