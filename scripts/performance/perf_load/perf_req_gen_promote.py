from indy import ledger
import json
import asyncio
import testinfra

from perf_load.perf_req_gen import RequestGenerator
from perf_load.perf_utils import PoolRegistry


class RGPromoteNode(RequestGenerator):
    _req_types = ["0"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pool_registry = PoolRegistry()

    def _rand_data(self):
        # pick current node from PoolRegistry to promote it
        result = self._pool_registry.current_node
        return result

    async def _gen_req(self, submitter_did, req_data):
        # promotion shift from demotions
        await asyncio.sleep(self._pool_registry.promotion_shift)
        data = {
            'alias': req_data['node_alias'],
            'services': ['VALIDATOR']
        }
        return await ledger.build_node_request(submitter_did, req_data['node_dest'], json.dumps(data))

    async def on_request_replied(self, req_data, gen_req, resp_or_exp):
        # start promoted node
        host = testinfra.get_host('ssh://persistent_node' + req_data['node_alias'][4:])
        host.run('sudo systemctl start indy-node')
