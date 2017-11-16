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

import os
from multiprocessing import Process

import sys

from indy_common.config_util import getConfig
from indy_node.utils.node_runner import run_node

config = getConfig()

num_nodes = 7
details = [
    ('Node1', 9701, 9702),
    ('Node2', 9703, 9704),
    ('Node3', 9705, 9706),
    ('Node4', 9707, 9708),
    ('Node5', 9709, 9710),
    ('Node6', 9711, 9712),
    ('Node7', 9713, 9714),
]


def start():
    sys.stdout = open(os.devnull, 'w')
    processes = []

    print('Going to start {} nodes'.format(num_nodes), file=sys.stderr)

    for (nm, np, cp) in details[:num_nodes]:
        p = Process(target=run_node, args=(config, nm, np, cp))
        p.start()
        processes.append(p)

    print('Started {} nodes'.format(num_nodes), file=sys.stderr)

    for p in processes:
        p.join()


if __name__ == '__main__':
    start()
