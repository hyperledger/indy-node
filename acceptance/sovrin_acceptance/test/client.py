import json

from indy import ledger, signus


class Client:
    def __init__(self, pool_handle, wallet_handle):
        self._pool_handle = pool_handle
        self._wallet_handle = wallet_handle
        self._active_did = None

    async def use_did(self, did):
        self._active_did = did

    async def new_did(self, did=None, seed=None):
        did_params = {}
        if did:
            did_params['did'] = did
        if seed:
            did_params['seed'] = seed

        did, verkey, _ = \
            await signus.create_and_store_my_did(self._wallet_handle,
                                                 json.dumps(did_params))

        await self.use_did(did)

        return did, verkey

    async def send_nym(self, dest, verkey=None, role=None):
        nym_req_json = await ledger.build_nym_request(self._active_did,
                                                      dest, verkey, None, role)
        await self._sign_and_submit_request(nym_req_json)

    async def send_get_nym(self, dest):
        get_nym_req_json = await ledger.build_get_nym_request(self._active_did,
                                                              dest)
        return await self._submit_request(get_nym_req_json)

    async def _sign_and_submit_request(self, request_json):
        response_json = \
            await ledger.sign_and_submit_request(self._pool_handle,
                                                 self._wallet_handle,
                                                 self._active_did,
                                                 request_json)
        return Client._extract_result(response_json)

    async def _submit_request(self, request_json):
        response_json = await ledger.submit_request(self._pool_handle,
                                                    request_json)
        return Client._extract_result(response_json)

    @staticmethod
    def _extract_result(response_json):
        response = json.loads(response_json)

        if 'result' in response and 'data' in response['result']:
            return json.loads(response['result']['data'])
        else:
            return None
