#!/usr/bin/python3

import select
import socket
import os
import subprocess
import shutil
from sovrin_node.utils.migration_tool import migrate
from stp_core.common.log import getlogger
from sovrin_node.server.upgrader import Upgrader

logger = getlogger()


TIMEOUT = 300
BASE_DIR = '/home/sovrin/'
BACKUP_FORMAT = 'zip'


class NodeControlTool:
    def __init__(self, timeout: int = TIMEOUT, base_dir: str = BASE_DIR, backup_format: str = BACKUP_FORMAT, test_mode: bool = False):
        self.test_mode = test_mode
        self.timeout = timeout
        self.base_dir = base_dir
        self.sovrin_dir = os.path.join(self.base_dir, '.sovrin')
        self.backup_format = backup_format

        # Create a TCP/IP socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setblocking(0)

        # Bind the socket to the port
        self.server_address = ('localhost', 30003)

        logger.info('Node control tool is starting up on {} port {}'.format(*self.server_address))
        self.server.bind(self.server_address)

        # Listen for incoming connections
        self.server.listen(1)

    @staticmethod
    def _compose_cmd(cmd):
        if os.name != 'nt':
            cmd = ' '.join(cmd)
        return cmd

    def _get_deps_list(self, package):
        logger.info('Getting dependencies for {}'.format(package))
        ret = subprocess.run(self.__class__._compose_cmd(['get_package_dependencies_ubuntu', package]), shell=True, check=True, universal_newlines=True, stdout=subprocess.PIPE, timeout=TIMEOUT)
        
        if ret.returncode != 0:
            msg = 'Upgrade failed: _get_deps_list returned {}'.format(ret.returncode)
            logger.error(msg)
            raise Exception(msg)
        
        return ret.stdout.strip()

    def _call_upgrade_script(self, version):
        logger.info('Upgrading sovrin node to version {}, test_mode {}'.format(version, int(self.test_mode)))

        deps = self._get_deps_list('indy-node={}'.format(version))
        deps = '"{}"'.format(deps)

        cmd_file = 'upgrade_sovrin_node'
        if self.test_mode:
            cmd_file = 'upgrade_sovrin_node_test'
        ret = subprocess.run(self.__class__._compose_cmd([cmd_file, deps]), shell=True, timeout=self.timeout)

        if ret.returncode != 0:
            msg = 'Upgrade failed: _upgrade script returned {}'.format(ret.returncode)
            logger.error(msg)
            raise Exception(msg)

    def _call_restart_node_script(self):
        logger.info('Restarting sovrin')
        ret = subprocess.run(self.__class__._compose_cmd(['restart_sovrin_node']), shell=True, timeout=self.timeout)
        if ret.returncode != 0:
            msg = 'Restart failed: script returned {}'.format(ret.returncode)
            logger.error(msg)
            raise Exception(msg)

    def _backup_name(self, version):
        return os.path.join(self.base_dir, 'sovrin_backup_{}'.format(version))

    def _backup_name_ext(self, version):
        return '{}.{}'.format(self._backup_name(version), self.backup_format)

    def _create_backup(self, version):
        shutil.make_archive(self._backup_name(version), self.backup_format, self.sovrin_dir)

    def _restore_from_backup(self, version):
        shutil.unpack_archive(self._backup_name_ext(version), self.sovrin_dir, self.backup_format)

    def _remove_backup(self, version):
        os.remove(self._backup_name_ext(version))

    def _migrate(self, current_version, new_version):
        migrate(current_version, new_version, self.timeout)

    def _do_migration(self, current_version, new_version):
        try:
            self._create_backup(current_version)
            self._migrate(current_version, new_version)
        except Exception as e:
            self._restore_from_backup(current_version)
            raise e
        finally:
            self._remove_backup(current_version)

    def _upgrade(self, new_version, migrate=True, rollback=True):
        try:
            current_version = Upgrader.getVersion()
            logger.info('Trying to upgrade from {} to {}'.format(current_version, new_version))
            self._call_upgrade_script(new_version)
            if migrate:
                self._do_migration(current_version, new_version)
            self._call_restart_node_script()
        except Exception as e:
            logger.error("Unexpected error in _upgrade {}, trying to rollback to the previous version {}".format(e, current_version))
            if rollback:
                self._upgrade(current_version, rollback=False)

    def _process_data(self, data):
        import json
        try:
            command = json.loads(data.decode("utf-8"))
            logger.debug("Decoded ", command)
            new_version = command['version']
            self._upgrade(new_version)
        except json.decoder.JSONDecodeError as e:
            logger.error("JSON decoding failed: {}".format(e))
        except Exception as e:
            logger.error("Unexpected error in process_data {}".format(e))

    def start(self):
        # Sockets from which we expect to read
        readers = [ self.server ]

        # Sockets to which we expect to write
        writers = [ ]
        errs = [ ]

        while readers:
            # Wait for at least one of the sockets to be ready for processing
            logger.debug('Waiting for the next event')
            readable, writable, exceptional = select.select(readers, writers, errs)
            for s in readable:
                if s is self.server:
                    # A "readable" server socket is ready to accept a connection
                    connection, client_address = s.accept()
                    logger.debug('New connection from {} on fd {}'.format(client_address,
                                                               connection.fileno()))
                    connection.setblocking(0)
                    readers.append(connection)
                else:
                    data = s.recv(8192)
                    if data:
                        logger.debug('Received "{}" from {} on fd {}'.format(data,
                                                                  s.getpeername(),
                                                                  s.fileno()))
                        self._process_data(data)
                    else:
                        logger.debug('Closing socket with fd {}'.format(s.fileno()))
                        readers.remove(s)
                        s.close()


