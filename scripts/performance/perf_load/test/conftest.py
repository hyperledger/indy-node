import pytest
import shutil
from perf_load.perf_client import LoadClient
from perf_load.perf_req_gen import RequestGenerator
from perf_load.perf_utils import random_string


class RGTestReq(RequestGenerator):
    reqs_gen = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def _gen_req(self, submit_did, req_data):
        RGTestReq.reqs_gen += 1
        return req_data


class LoadClientTest(LoadClient):
    reqs_snd = 0
    clients = 0

    def __init__(self, *args, **kwargs):
        LoadClientTest.clients += 1
        super().__init__(*args, **kwargs)

    async def pool_open_pool(self, name, config):
        return 42

    async def wallet_create_wallet(self, config, credential):
        pass

    async def wallet_open_wallet(self, config, credential):
        return 42

    async def did_create_my_did(self, wallet_h, cfg):
        return 42, 42

    async def ledger_sign_req(self, wallet_h, did, req):
        return req + " signed"

    async def ledger_submit(self, pool_h, req):
        LoadClientTest.reqs_snd += 1
        return 42

    async def pool_close_pool(self, pool_h):
        pass

    async def pool_protocol_version(self):
        pass

    async def pool_create_config(self, name, cfg):
        pass

    async def wallet_close(self, wallet_h):
        pass

    async def _init_pool(self, genesis_path):
        pass

    async def _wallet_init(self, w_key):
        pass

    async def _did_init(self, seed):
        pass

    async def _pre_init(self):
        pass

    async def _post_init(self):
        pass


@pytest.fixture(scope="function")
def tmpdir(request):
    tmp_h = request.config._tmpdirhandler
    x = str(tmp_h.mktemp(random_string(4), numbered=True))
    yield x
    shutil.rmtree(x)
