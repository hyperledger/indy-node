#!/usr/bin/python3

import select
import socket
import os
import subprocess
import shutil
import re
from typing import List
from sovrin_node.utils.migration_tool import migrate
from stp_core.common.log import getlogger
from sovrin_node.server.upgrader import Upgrader
from sovrin_common.config_util import getConfig

logger = getlogger()


TIMEOUT = 300
BASE_DIR = '/home/sovrin/'
BACKUP_FORMAT = 'zip'
DEPS = ['indy-plenum', 'indy-anoncreds']
CONFIG = getConfig()
FILES_TO_PRESERVE = [CONFIG.lastRunVersionFile, CONFIG.nextVersionFile,
                     CONFIG.upgradeLogFile, CONFIG.lastVersionFilePath]
BACKUP_NAME_PREFIX = 'sovrin_backup_'
BACKUP_NUM = 10
PACKAGES_TO_HOLD = 'indy-anoncreds indy-plenum indy-node'


class NodeControlTool:
    MAX_LINE_SIZE = 1024

    def __init__(
            self,
            timeout: int = TIMEOUT,
            base_dir: str = BASE_DIR,
            backup_format: str = BACKUP_FORMAT,
            test_mode: bool = False,
            deps: List[str] = DEPS,
            files_to_preserve: List[str] = FILES_TO_PRESERVE,
            backup_name_prefix: str = BACKUP_NAME_PREFIX,
            backup_num: int = BACKUP_NUM,
            hold_ext: str = ''):
        self.test_mode = test_mode
        self.timeout = timeout
        self.base_dir = base_dir
        self.sovrin_dir = os.path.join(self.base_dir, '.sovrin')
        self.tmp_dir = os.path.join(self.base_dir, '.sovrin_tmp')
        self.backup_format = backup_format
        self.deps = deps
        self.files_to_preserve = files_to_preserve
        self.backup_num = backup_num
        self.backup_name_prefix = backup_name_prefix
        self.packages_to_hold = ' '.join([PACKAGES_TO_HOLD, hold_ext])

        # Create a TCP/IP socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.setblocking(0)

        # Bind the socket to the port
        self.server_address = ('localhost', 30003)

        logger.info('Node control tool is starting up on {} port {}'.format(
            *self.server_address))
        self.server.bind(self.server_address)

        # Listen for incoming connections
        self.server.listen(1)

    @staticmethod
    def _compose_cmd(cmd):
        if os.name != 'nt':
            cmd = ' '.join(cmd)
        return cmd

    @classmethod
    def _get_info_from_package_manager(cls, package):
        ret = subprocess.run(
            cls._compose_cmd(
                [
                    'apt-cache',
                    'show',
                    package]),
            shell=True,
            check=True,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            timeout=TIMEOUT)

        if ret.returncode != 0:
            msg = 'Upgrade failed: _get_deps_list returned {}'.format(
                ret.returncode)
            logger.error(msg)
            raise Exception(msg)

        return ret.stdout.strip()

    @classmethod
    def _update_package_cache(cls):
        ret = subprocess.run(
            cls._compose_cmd(
                [
                    'apt',
                    'update']),
            shell=True,
            check=True,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            timeout=TIMEOUT)

        if ret.returncode != 0:
            msg = 'Upgrade failed: _get_deps_list returned {}'.format(
                ret.returncode)
            logger.error(msg)
            raise Exception(msg)

        return ret.stdout.strip()

    def _hold_packages(self):
        ret = subprocess.run(
            self._compose_cmd(
                [
                    'apt-mark',
                    'hold',
                    self.packages_to_hold]),
            shell=True,
            check=True,
            universal_newlines=True,
            stdout=subprocess.PIPE,
            timeout=TIMEOUT)

        if ret.returncode != 0:
            msg = 'Holding {} packages failed: _hold_packages returned {}'.format(
                self.packages_to_hold, ret.returncode)
            logger.error(msg)
            raise Exception(msg)

        logger.info('Successfully put {} packages on hold'.format(
            self.packages_to_hold))

    def _get_deps_list(self, package):
        logger.info('Getting dependencies for {}'.format(package))
        ret = ''
        self._update_package_cache()
        package_info = self._get_info_from_package_manager(package)

        for dep in self.deps:
            if dep in package_info:
                match = re.search(
                    '.*{} \(= ([0-9]+\.[0-9]+\.[0-9]+)\).*'.format(dep),
                    package_info)
                if match:
                    dep_version = match.group(1)
                    dep_package = '{}={}'.format(dep, dep_version)
                    dep_tree = self._get_deps_list(dep_package)
                    ret = '{} {}'.format(dep_tree, ret)

        ret = '{} {}'.format(ret, package)
        return ret

    def _call_upgrade_script(self, version):
        logger.info('Upgrading sovrin node to version {}, test_mode {}'.format(
            version, int(self.test_mode)))

        deps = self._get_deps_list('indy-node={}'.format(version))
        deps = '"{}"'.format(deps)

        cmd_file = 'upgrade_sovrin_node'
        if self.test_mode:
            cmd_file = 'upgrade_sovrin_node_test'
        ret = subprocess.run(self._compose_cmd(
            [cmd_file, deps]), shell=True, timeout=self.timeout)

        if ret.returncode != 0:
            msg = 'Upgrade failed: _upgrade script returned {}'.format(
                ret.returncode)
            logger.error(msg)
            raise Exception(msg)

    def _call_restart_node_script(self):
        logger.info('Restarting sovrin')
        ret = subprocess.run(self._compose_cmd(
            ['restart_sovrin_node']), shell=True, timeout=self.timeout)
        if ret.returncode != 0:
            msg = 'Restart failed: script returned {}'.format(ret.returncode)
            logger.error(msg)
            raise Exception(msg)

    def _backup_name(self, version):
        return os.path.join(self.base_dir, '{}{}'.format(
            self.backup_name_prefix, version))

    def _backup_name_ext(self, version):
        return '{}.{}'.format(self._backup_name(version), self.backup_format)

    def _create_backup(self, version):
        logger.debug('Creating backup for {}'.format(version))
        shutil.make_archive(self._backup_name(version),
                            self.backup_format, self.sovrin_dir)

    def _restore_from_backup(self, version):
        logger.debug('Restoring from backup for {}'.format(version))
        for file_path in self.files_to_preserve:
            try:
                shutil.copy2(os.path.join(self.sovrin_dir, file_path),
                             os.path.join(self.tmp_dir, file_path))
            except IOError as e:
                logger.warning(
                    'Copying {} failed due to {}'.format(file_path, e))
        shutil.unpack_archive(self._backup_name_ext(
            version), self.sovrin_dir, self.backup_format)
        for file_path in self.files_to_preserve:
            try:
                shutil.copy2(os.path.join(self.tmp_dir, file_path),
                             os.path.join(self.sovrin_dir, file_path))
            except IOError as e:
                logger.warning(
                    'Copying {} failed due to {}'.format(file_path, e))
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _get_backups(self):
        files = [os.path.join(self.base_dir, file)
                 for file in os.listdir(self.base_dir)]
        files = [file for file in files if os.path.isfile(
            file) and self.backup_name_prefix in file]
        return sorted(files, key=os.path.getmtime, reverse=True)

    def _remove_old_backups(self):
        logger.debug('Removing old backups')
        files = self._get_backups()
        if len(files):
            files = files[self.backup_num:]
        for file in files:
            os.remove(file)

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
            self._remove_old_backups()

    def _upgrade(self, new_version, migrate=True, rollback=True):
        try:
            current_version = Upgrader.getVersion()
            logger.info('Trying to upgrade from {} to {}'.format(
                current_version, new_version))
            self._call_upgrade_script(new_version)
            if migrate:
                self._do_migration(current_version, new_version)
            self._call_restart_node_script()
        except Exception as e:
            logger.error(
                "Unexpected error in _upgrade {}, trying to rollback to the previous version {}".format(
                    e, current_version))
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
        self._hold_packages()

        # Sockets from which we expect to read
        readers = [self.server]

        # Sockets to which we expect to write
        writers = []
        errs = []

        while readers:
            # Wait for at least one of the sockets to be ready for processing
            logger.debug('Waiting for the next event')
            readable, writable, exceptional = select.select(
                readers, writers, errs)
            for s in readable:
                if s is self.server:
                    # A "readable" server socket is ready to accept a
                    # connection
                    connection, client_address = s.accept()
                    logger.debug(
                        'New connection from {} on fd {}'.format(
                            client_address, connection.fileno()))
                    connection.setblocking(0)
                    readers.append(connection)
                else:
                    data = s.recv(8192)
                    if data:
                        logger.debug(
                            'Received "{}" from {} on fd {}'.format(
                                data, s.getpeername(), s.fileno()))
                        self._process_data(data)
                    else:
                        logger.debug(
                            'Closing socket with fd {}'.format(s.fileno()))
                        readers.remove(s)
                        s.close()
