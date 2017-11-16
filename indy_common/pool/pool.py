class Pool:

    @property
    def genesis_transactions(self):
        raise NotImplementedError

    def create_client(self, port: int):
        raise NotImplementedError
