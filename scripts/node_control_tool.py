#!/usr/bin/python3

import select
import socket
import argparse
import os
import timeout_decorator
import subprocess
from migration_tool import migrate
from stp_core.common.log import getlogger
from sovrin_node.server.upgrader import Upgrader

logger = getlogger()

TIMEOUT=300


def compose_cmd(cmd):
    if os.name != 'nt':
        cmd = ' '.join(cmd)
    return cmd


def get_deps_list(package):
    logger.info('Getting dependencies for {}'.format(package))
    ret = subprocess.run(compose_cmd(['get_package_dependencies_ubuntu', package]), shell=True, check=True, universal_newlines=True, timeout=TIMEOUT)
    return ret.stdout

def call_upgrade_script(version):
    logger.info('Upgrading sovrin node to version {}, test_mode {}'.format(version, int(test_mode)))

    deps = get_deps_list('sovrin-node={}'.format(version))

    cmd_file = 'upgrade_sovrin_node'
    if test_mode:
        cmd_file = 'upgrade_sovrin_node_test'
    ret = subprocess.run(compose_cmd([cmd_file, deps]), shell=True, timeout=TIMEOUT)

    if ret.returncode != 0:
        msg = 'Upgrade failed: upgrade script returned {}'.format(retcode)
        logger.error(msg)
        raise Exception(msg)


def call_restart_node_script():
    logger.info('Restarting sovrin')
    ret = subprocess.run(compose_cmd(['restart_sovrin_node']), shell=True, timeout=TIMEOUT)
    if ret.returncode != 0:
        msg = 'Restart failed: script returned {}'.format(retcode)
        logger.error(msg)
        raise Exception(msg)


@timeout_decorator.timeout(TIMEOUT)
def do_migration(current_version):
    migrate(current_version)


def upgrade(new_version, migrate=True, rollback=True):
    try:
        current_version = Upgrader.getVersion()
        call_upgrade_script(new_version)
        if migrate:
            do_migration(current_version)
        call_restart_node_script()
    except Exception as e:
        logger.error("Unexpected error in upgrade {}, trying to rollback to the previous version {}".format(e, current_version))
        if rollback:
            upgrade(current_version, migrate=False, rollback=False)


def process_data(data):
    import json
    try:
        command = json.loads(data.decode("utf-8"))
        logger.debug("Decoded ", command)
        new_version = command['version']
        upgrade(new_version)
    except json.decoder.JSONDecodeError as e:
        logger.error("JSON decoding failed: {}".format(e))
    except Exception as e:
        logger.error("Unexpected error in process_data {}".format(e))


# Parse command line arguments
test_mode = False
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--test", help="runs in special Test mode",
                    action="store_true")
args = parser.parse_args()
if args.test:
    test_mode = True

# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.setblocking(0)

# Bind the socket to the port
server_address = ('localhost', 30003)
logger.info('Node control tools is starting up on %s port %s' % server_address)
server.bind(server_address)

# Listen for incoming connections
server.listen(1)

# Sockets from which we expect to read
readers = [ server ]

# Sockets to which we expect to write
writers = [ ]
errs = [ ]

while readers:
    # Wait for at least one of the sockets to be ready for processing
    logger.debug('\nwaiting for the next event')
    readable, writable, exceptional = select.select(readers, writers, errs)
    for s in readable:
        if s is server:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = s.accept()
            logger.debug('new connection from %s on fd %d' % (client_address,
                                                       connection.fileno()))
            connection.setblocking(0)
            readers.append(connection)
        else:
            data = s.recv(8192)
            if data:
                logger.debug('received "%s" from %s on fd %d' % (data,
                                                          s.getpeername(),
                                                          s.fileno()))
                process_data(data)
            else:
                logger.debug('closing socket with fd %d' % (s.fileno()))
                readers.remove(s)
                s.close()


