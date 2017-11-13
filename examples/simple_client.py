#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

#! /usr/bin/env python3
"""
This is a simple script to demonstrate a client connecting to a running
consensus pool. To see it in action, run simple_node.py in four separate
terminals, and in a fifth one, run this script.

TODO: create client
TODO: demonstrate client verification key bootstrapping
"""
import os
import tempfile
from collections import OrderedDict

from stp_core.loop.looper import Looper
from plenum.common.signer_simple import SimpleSigner

from indy_client.client.client import Client
from indy_common.constants import TXN_TYPE, NYM


def run_node():
    ip = '52.37.111.254'
    cliNodeReg = OrderedDict([
        # ('AlphaC', ('127.0.0.1', 8002)),
        ('AlphaC', (ip, 4002)),
        ('BetaC', (ip, 4004)),
        ('GammaC', (ip, 4006)),
        ('DeltaC', (ip, 4008))
    ])

    with Looper(debug=False) as looper:
        # Nodes persist keys when bootstrapping to other nodes and reconnecting
        # using an ephemeral temporary directory when proving a concept is a
        # nice way to keep things clean.
        clientName = 'Joem'

        # this seed is used by the signer to deterministically generate
        # a signature verification key that is shared out of band with the
        # consensus pool
        seed = b'g034OTmx7qBRtywvCbKhjfALHnsdcJpl'
        assert len(seed) == 32
        signer = SimpleSigner(seed=seed)
        assert signer.verstr == 'o7z4QmFkNB+mVkFI2BwX0H' \
                                'dm1BGhnz8psWnKYIXWTaQ='

        client_address = ('0.0.0.0', 8000)

        tmpdir = os.path.join(tempfile.gettempdir(), "indy_clients",
                              clientName)
        client = Client(clientName,
                        cliNodeReg,
                        ha=client_address,
                        signer=signer,
                        basedirpath=tmpdir)
        looper.add(client)

        # give the client time to connect
        looper.runFor(3)

        # a simple message
        msg = {TXN_TYPE: NYM}

        # submit the request to the pool
        request, = client.submit(msg)

        # allow time for the request to be executed
        looper.runFor(3)

        reply, status = client.getReply(request.reqId)
        print('')
        print('Reply: {}\n'.format(reply))
        print('Status: {}\n'.format(status))


if __name__ == '__main__':
    run_node()
