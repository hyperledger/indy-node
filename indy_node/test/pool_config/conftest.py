import pytest

from indy_node.test.pool_config.helper import sdk_ensure_pool_config_sent


def genPoolConfig(writes: bool, force: bool):
    return dict(writes=writes, force=force)


@pytest.fixture(scope='module')
def poolConfigWTFF():
    return genPoolConfig(writes=True, force=False)


@pytest.fixture(scope='module')
def poolConfigWFFF():
    return genPoolConfig(writes=False, force=False)


@pytest.fixture(scope='module')
def poolConfigWTFT():
    return genPoolConfig(writes=True, force=True)


@pytest.fixture(scope='module')
def poolConfigWFFT():
    return genPoolConfig(writes=False, force=True)


@pytest.fixture(scope="module")
def poolConfigSent(looper, nodeSet, sdk_pool_handle, sdk_wallet_trustee, poolCfg):
    sdk_ensure_pool_config_sent(looper, sdk_pool_handle, sdk_wallet_trustee, poolCfg)
