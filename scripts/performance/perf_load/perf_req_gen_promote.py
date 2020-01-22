from indy import ledger
import json
import asyncio
import testinfra

from perf_load.perf_req_gen import RequestGenerator
from perf_load.perf_utils import PoolRegistry
from perf_load.perf_processes import tr


class RGPromoteNode(RequestGenerator):
    _req_types = ["0"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _rand_data(self):
        # pick current node from PoolRegistry to promote it
        result = PoolRegistry(tr.genesis_path).current_node
        return result

    async def _gen_req(self, submitter_did, req_data):
        # promotion shift from demotions
        await asyncio.sleep(tr.promotion_shift)
        data = {
            'alias': req_data['node_alias'],
            'services': ['VALIDATOR']
        }
        return await ledger.build_node_request(submitter_did, req_data['node_dest'], json.dumps(data))

    async def on_request_replied(self, req_data, gen_req, resp_or_exp):
        # restart promoted node
        host = testinfra.get_host('ssh://persistent_node' + req_data['node_alias'][4:])
        host.run('sudo systemctl restart indy-node')
