#!/usr/bin/python3

import select
import socket
import argparse
import os


def compose_cmd(cmd):
    if os.name != 'nt':
        cmd = ' '.join(cmd)
    return cmd


def call_upgrade_script(version):
    import subprocess
    print('Upgrading sovrin node to version %s, test_mode %d ' % (version, int(test_mode)))
    try:
        if test_mode:
            retcode = subprocess.call(compose_cmd(['upgrade_sovrin_node_test', version]), shell=True)
        else:
            retcode = subprocess.call(compose_cmd(['upgrade_sovrin_node', version]), shell=True)
        if retcode != 0:
            print('Upgrade failed')
    except:
        print('Something went wrong with calling upgrade script')


def process_data(data):
    import json
    try:
        command = json.loads(data.decode("utf-8"))
        print("Decoded ", command)
        version = command['version']
        call_upgrade_script(version)
    except json.decoder.JSONDecodeError:
        print("JSON decoding failed. Skip this command")
    except:
        print("Unexpected error in function below. Pass it")
        pass

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
print('starting up on %s port %s' % server_address)
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
    print('\nwaiting for the next event')
    readable, writable, exceptional = select.select(readers, writers, errs)
    for s in readable:
        if s is server:
            # A "readable" server socket is ready to accept a connection
            connection, client_address = s.accept()
            print('new connection from %s on fd %d' % (client_address,
                                                       connection.fileno()))
            connection.setblocking(0)
            readers.append(connection)
        else:
            data = s.recv(8192)
            if data:
                print('received "%s" from %s on fd %d' % (data,
                                                          s.getpeername(),
                                                          s.fileno()))
                process_data(data)
            else:
                print('closing socket with fd %d' % (s.fileno()))
                readers.remove(s)
                s.close()


