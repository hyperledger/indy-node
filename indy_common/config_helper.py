import os

class NodeConfigHelper():
    def __init__(self, name: str, config, network_name: str=None):
        assert name is not None
        assert config is not None
        self.name = name
        self.config = config
        self.network_name = network_name or config.CURRENT_NETWORK

    @property
    def ledger_dir(self):
        return os.path.join(self.config.LEDGER_DIR, self.network_name, 'data', self.name)

    @property
    def log_dir(self):
        return os.path.join(self.config.LOG_DIR, self.network_name)

    @property
    def keys_dir(self):
        return os.path.join(self.config.KEYS_DIR, self.network_name, 'keys', self.name)

    @property
    def genesis_dir(self):
        return os.path.join(self.config.GENESIS_DIR, self.network_name)

    @property
    def plugins_dir(self):
        return self.config.PLUGINS_DIR


class ClientConfigHelper(NodeConfigHelper):
    @property
    def log_dir(self):
        return self.config.LOG_DIR

    @property
    def wallet_dir(self):
        return os.path.join(self.config.WALLET_DIR, self.network_name)
