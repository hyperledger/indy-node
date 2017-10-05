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
