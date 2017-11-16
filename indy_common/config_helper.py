import os

from plenum.common.config_helper import PConfigHelper


class ConfigHelper(PConfigHelper):

    @property
    def log_dir(self):
        return self.chroot_if_needed(
            os.path.join(self.config.LOG_DIR, self.config.NETWORK_NAME))

    @property
    def genesis_dir(self):
        return self.chroot_if_needed(
            os.path.join(self.config.GENESIS_DIR, self.config.NETWORK_NAME))

    @property
    def keys_dir(self):
        return self.chroot_if_needed(
            os.path.join(self.config.KEYS_DIR, self.config.NETWORK_NAME, 'keys'))



class NodeConfigHelper(ConfigHelper):

    def __init__(self, name: str, config, *, chroot='/'):
        assert name is not None
        super().__init__(config, chroot=chroot)
        self.name = name

    @property
    def ledger_dir(self):
        return self.chroot_if_needed(
            os.path.join(self.config.LEDGER_DIR, self.config.NETWORK_NAME, 'data', self.name))
