import logging
from time import perf_counter

from plenum.common.signer_did import DidSigner
from indy_client.client.client import Client
from indy_client.client.wallet.wallet import Wallet
from indy_common.identity import Identity
from stp_core.common.log import getlogger, Logger
from stp_core.network.port_dispenser import genHa, HA
from stp_core.loop.looper import Looper
from plenum.test.helper import waitForSufficientRepliesForRequests
from indy_common.config_util import getConfig

numReqs = 100
splits = 1

Logger.setLogLevel(logging.WARNING)
logger = getlogger()


def sendRandomRequests(wallet: Wallet, client: Client, count: int):
    print('{} random requests will be sent'.format(count))
    for i in range(count):
        idr, signer = wallet.addIdentifier()
        idy = Identity(identifier=idr,
                       verkey=signer.verkey)
        wallet.addTrustAnchoredIdentity(idy)
    reqs = wallet.preparePending()
    return client.submitReqs(*reqs)[0]


def put_load():
    port = genHa()[1]
    ha = HA('0.0.0.0', port)
    name = "hello"
    wallet = Wallet(name)
    wallet.addIdentifier(
        signer=DidSigner(seed=b'000000000000000000000000Steward1'))
    client = Client(name, ha=ha)
    with Looper(debug=getConfig().LOOPER_DEBUG) as looper:
        looper.add(client)
        print('Will send {} reqs in all'.format(numReqs))
        requests = sendRandomRequests(wallet, client, numReqs)
        start = perf_counter()
        for i in range(0, numReqs, numReqs // splits):
            print('Will wait for {} now'.format(numReqs // splits))
            s = perf_counter()
            reqs = requests[i:i + numReqs // splits + 1]
            waitForSufficientRepliesForRequests(looper, client, requests=reqs,
                                                customTimeoutPerReq=100,
                                                override_timeout_limit=True)
            print('>>> Got replies for {} requests << in {}'.
                  format(numReqs // splits, perf_counter() - s))
        end = perf_counter()
        print('>>>Total {} in {}<<<'.format(numReqs, end - start))
        exit(0)


if __name__ == "__main__":
    put_load()
