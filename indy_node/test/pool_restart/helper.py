import asyncio
import json
import socket
from indy.did import create_and_store_my_did
from indy.error import ErrorCode
from indy.ledger import build_pool_restart_request

from plenum.common.util import randomString
from plenum.test.helper import sdk_get_replies, sdk_check_reply
from plenum.test.pool_transactions.helper import sdk_sign_and_send_prepared_request
from stp_core.common.log import getlogger

from indy_common.constants import MESSAGE_TYPE, \
    RESTART_MESSAGE
from indy_common.config import controlServiceHost, controlServicePort

logger = getlogger()


def compose_restart_message(action):
    return (json.dumps({MESSAGE_TYPE: RESTART_MESSAGE})).encode()


def send_restart_message(action):
    sock = socket.create_connection(
        (controlServiceHost, controlServicePort))
    sock.sendall(compose_restart_message(action))
    sock.close()


async def _createServer(host, port):
    """
    Create async server that listens host:port, reads client request and puts
    value to some future that can be used then for checks

    :return: reference to server and future for request
    """
    indicator = asyncio.Future()

    async def _handle(reader, writer):
        raw = await reader.readline()
        request = raw.decode("utf-8")
        indicator.set_result(request)
    server = await asyncio.start_server(_handle, host, port)
    return server, indicator


def _stopServer(server):
    print('Closing server')
    server.close()
    # def _stop(x):
    #     print('Closing server')
    #     server.close()
    # return _stop


def _checkFuture(future):
    """
    Wrapper for futures that lets checking of their status using 'eventually'
    """
    def _check():
        if future.cancelled():
            return None
        if future.done():
            return future.result()
        raise Exception()
    return _check


def sdk_send_restart(looper, trusty_wallet, sdk_pool_handle,
                     action=None, datetime=None, seed=None):
    # filling restart request and getting trusty did
    seed = seed or randomString(32)
    restart_request, did = looper.loop.run_until_complete(
        prepare_restart_request(trusty_wallet, seed, action, datetime))

    # sending request using 'sdk_' functions
    request_couple = sdk_sign_and_send_prepared_request(looper, trusty_wallet,
                                                        sdk_pool_handle,
                                                        restart_request)
    # waiting for replies
    return sdk_get_and_check_multiply_replies(looper, request_couple)


def sdk_get_and_check_multiply_replies(looper, request_couple):
    rets = []
    for req_res in sdk_get_replies(looper, [request_couple, ]):
        req, responses = req_res
        if not isinstance(responses, ErrorCode) and "op" not in responses:
            for node_resp in responses.values():
                sdk_check_reply((req, json.loads(node_resp)))
        else:
            sdk_check_reply(req_res)
        rets.append(req_res)
    return rets[0]


async def prepare_restart_request(wallet, named_seed, action="start",
                                  restart_time="0"):
    wh, submitter_did = wallet
    (named_did, named_verkey) = \
        await create_and_store_my_did(wh, json.dumps({'seed': named_seed}))
    restart_request = await build_pool_restart_request(submitter_did,
                                                       action,
                                                       restart_time)
    return restart_request, named_did

