

class ClientReady:
    pass


class ClientRun:
    pass


class ClientStop:
    pass


class ClientGetStat:
    pass


class ClientSend:
    def __init__(self, cnt: int = 10):
        self.cnt = cnt
