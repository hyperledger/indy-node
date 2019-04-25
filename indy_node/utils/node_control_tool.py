import os
import select
import shutil
import socket
from typing import List

from indy_common.constants import UPGRADE_MESSAGE, RESTART_MESSAGE, MESSAGE_TYPE
from stp_core.common.log import getlogger

from indy_common.version import (
    PackageVersion, SourceVersion, src_version_cls
)
from indy_common.config_util import getConfig
from indy_common.config_helper import ConfigHelper
from indy_common.util import compose_cmd
from indy_node.utils.migration_tool import migrate
from indy_node.utils.node_control_utils import NodeControlUtil

logger = getlogger()

TIMEOUT = 300
BACKUP_FORMAT = 'zip'
BACKUP_NUM = 10
TMP_DIR = '/tmp/.indy_tmp'


class NodeControlTool:
    MAX_LINE_SIZE = 1024

    def __init__(
            self,
            timeout: int = TIMEOUT,
            backup_format: str = BACKUP_FORMAT,
            test_mode: bool = False,
            backup_target: str = None,
            files_to_preserve: List[str] = None,
            backup_dir: str = None,
            backup_name_prefix: str = None,
            backup_num: int = BACKUP_NUM,
            hold_ext: str = '',
            config=None):
        self.config = config or getConfig()

        self.test_mode = test_mode
        self.timeout = timeout or TIMEOUT

        self.hold_ext = hold_ext.split(" ")

        config_helper = ConfigHelper(self.config)
        self.backup_dir = backup_dir or config_helper.backup_dir
        self.backup_target = backup_target or config_helper.genesis_dir

        self.tmp_dir = TMP_DIR
        self.backup_format = backup_format

        _files_to_preserve = [self.config.lastRunVersionFile, self.config.nextVersionFile,
                              self.config.upgradeLogFile, self.config.lastVersionFilePath,
                              self.config.restartLogFile]

        self.files_to_preserve = files_to_preserve or _files_to_preserve
        self.backup_num = backup_num

        _backup_name_prefix = '{}_backup_'.format(self.config.NETWORK_NAME)

        self.backup_name_prefix = backup_name_prefix or _backup_name_prefix

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

    def _get_deps_list(self, package):
        logger.info('Getting dependencies for {}'.format(package))
        NodeControlUtil.update_package_cache()
        app_holded = self.config.PACKAGES_TO_HOLD + self.hold_ext
        dep_tree = NodeControlUtil.get_deps_tree_filtered(package, filter_list=app_holded)
        ret = []
        NodeControlUtil.dep_tree_traverse(dep_tree, ret)
        # Filter deps according to system hold list
        # in case of hold empty return only package
        holded = NodeControlUtil.get_sys_holds()
        if not holded:
            return package
        else:
            ret_list = []
            for rl in ret:
                name = rl.split("=", maxsplit=1)[0]
                if name in holded:
                    ret_list.append(rl)
            if package not in ret_list:
                ret_list.append(package)
            return " ".join(ret_list)

    def _call_upgrade_script(self, pkg_name: str, pkg_ver: PackageVersion):
        logger.info(
            "Upgrading {} to package version {}, test_mode {}"
            .format(pkg_name, pkg_ver, int(self.test_mode))
        )

        deps = self._get_deps_list('{}={}'.format(pkg_name, pkg_ver))
        deps = '"{}"'.format(deps)

        cmd_file = 'upgrade_indy_node'
        if self.test_mode:
            cmd_file = 'upgrade_indy_node_test'

        cmd = compose_cmd([cmd_file, deps])
        NodeControlUtil.run_shell_script(cmd, timeout=self.timeout)

    def _call_restart_node_script(self):
        logger.info('Restarting indy')
        cmd = compose_cmd(['restart_indy_node'])
        NodeControlUtil.run_shell_script(cmd, timeout=self.timeout)

    def _backup_name(self, src_ver: str):
        return os.path.join(self.backup_dir, '{}{}'.format(
            self.backup_name_prefix, src_ver))

    def _backup_name_ext(self, src_ver: str):
        return '{}.{}'.format(self._backup_name(src_ver), self.backup_format)

    def _create_backup(self, src_ver: str):
        logger.debug('Creating backup for {}'.format(src_ver))
        shutil.make_archive(self._backup_name(src_ver),
                            self.backup_format, self.backup_target)

    def _restore_from_backup(self, src_ver: str):
        logger.info('Restoring from backup for {}'.format(src_ver))
        for file_path in self.files_to_preserve:
            try:
                shutil.copy2(os.path.join(self.backup_target, file_path),
                             os.path.join(self.tmp_dir, file_path))
            except IOError as e:
                logger.warning('Copying {} failed due to {}'
                               .format(file_path, e))
        shutil.unpack_archive(self._backup_name_ext(
            src_ver), self.backup_target, self.backup_format)
        for file_path in self.files_to_preserve:
            try:
                shutil.copy2(os.path.join(self.tmp_dir, file_path),
                             os.path.join(self.backup_target, file_path))
            except IOError as e:
                logger.warning('Copying {} failed due to {}'
                               .format(file_path, e))
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def _get_backups(self):
        files = [os.path.join(self.backup_dir, bk_file)
                 for bk_file in os.listdir(self.backup_dir)]
        files = [bk_file for bk_file in files if os.path.isfile(
            bk_file) and self.backup_name_prefix in bk_file]
        return sorted(files, key=os.path.getmtime, reverse=True)

    def _remove_old_backups(self):
        logger.display('Removing old backups')
        files = self._get_backups()
        if len(files):
            files = files[self.backup_num:]
        for file in files:
            os.remove(file)

    def _do_migration(self, curr_src_ver: str, new_src_ver: str):
        migrate(curr_src_ver, new_src_ver, self.timeout)

    def _migrate(self, curr_src_ver: str, new_src_ver: str):
        try:
            self._create_backup(curr_src_ver)
            self._do_migration(curr_src_ver, new_src_ver)
        except Exception as e:
            self._restore_from_backup(curr_src_ver)
            raise e
        self._remove_old_backups()

    def _do_upgrade(
            self,
            pkg_name: str,
            curr_pkg_ver: PackageVersion,
            new_pkg_ver: PackageVersion,
            rollback: bool
    ):
        from indy_node.server.upgrader import Upgrader
        cur_node_src_ver = Upgrader.get_src_version()
        logger.info(
            "Trying to upgrade from {}={} to {}"
            .format(pkg_name, curr_pkg_ver, new_pkg_ver)
        )

        try:
            self._call_upgrade_script(pkg_name, new_pkg_ver)
            if migrate:
                # TODO test for migration, should fail if nocache is False !!!
                new_node_src_ver = Upgrader.get_src_version(nocache=True)
                # assumption: migrations are anchored to release versions only
                self._migrate(cur_node_src_ver.release, new_node_src_ver.release)
            self._call_restart_node_script()
        except Exception as ex:
            logger.error(
                "Upgrade from {} to {} failed: {}"
                .format(curr_pkg_ver, new_pkg_ver, ex)
            )
            if rollback:
                logger.error("Trying to rollback to the previous version {}"
                             .format(ex, curr_pkg_ver))
                self._do_upgrade(
                    pkg_name, new_pkg_ver, curr_pkg_ver, rollback=False)

    # TODO test
    def _upgrade(
            self,
            new_src_ver: SourceVersion,
            pkg_name: str,
            migrate=True,
            rollback=True
    ):
        curr_pkg_ver, _ = NodeControlUtil.curr_pkg_info(pkg_name)

        if not curr_pkg_ver:
            logger.error("package {} is not found".format(pkg_name))
            return

        logger.info(
            "Current version of package '{}' is '{}'"
            .format(pkg_name, curr_pkg_ver)
        )

        new_pkg_ver = NodeControlUtil.get_latest_pkg_version(
            pkg_name, upstream=new_src_ver)
        if not new_pkg_ver:
            logger.error(
                "Upgrade from {} to upstream version {} failed: package {} for"
                " upstream version is not found"
                .format(curr_pkg_ver, new_src_ver, pkg_name)
            )
            return

        self._do_upgrade(pkg_name, curr_pkg_ver, new_pkg_ver, rollback)

    def _restart(self):
        try:
            self._call_restart_node_script()
        except Exception as ex:
            logger.error("Restart fail: " + ex.args[0])

    def _process_data(self, data):
        import json
        try:
            command = json.loads(data.decode("utf-8"))
            logger.debug("Decoded ", command)
            if command[MESSAGE_TYPE] == UPGRADE_MESSAGE:
                new_src_ver = command['version']
                pkg_name = command['pkg_name']
                self._upgrade(src_version_cls(pkg_name)(new_src_ver), pkg_name)
            elif command[MESSAGE_TYPE] == RESTART_MESSAGE:
                self._restart()
        except json.decoder.JSONDecodeError as e:
            logger.error("JSON decoding failed: {}".format(e))
        except Exception as e:
            logger.error("Unexpected error in _process_data {}".format(e))

    def start(self):
        NodeControlUtil.hold_packages(self.config.PACKAGES_TO_HOLD + self.hold_ext)

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
                    logger.debug('New connection from {} on fd {}'
                                 .format(client_address, connection.fileno()))
                    connection.setblocking(0)
                    readers.append(connection)
                else:
                    data = s.recv(8192)
                    if data:
                        logger.debug(
                            'Received "{}" from {} on fd {}'
                            .format(data, s.getpeername(), s.fileno()))
                        self._process_data(data)
                    else:
                        logger.debug('Closing socket with fd {}'
                                     .format(s.fileno()))
                        readers.remove(s)
                        s.close()
