import os
import select
import shutil
import socket
from typing import List

from indy_common.constants import UPGRADE_MESSAGE, RESTART_MESSAGE, MESSAGE_TYPE
from stp_core.common.log import getlogger

from indy_common.config_util import getConfig
from indy_common.config_helper import ConfigHelper
from indy_common.util import compose_cmd
from indy_node.utils.migration_tool import migrate
from indy_node.utils.node_control_utils import NodeControlUtil

logger = getlogger()

TIMEOUT = 300
BACKUP_FORMAT = 'zip'
DEPS = ['indy-plenum', 'indy-anoncreds', 'python3-indy-crypto']
BACKUP_NUM = 10
PACKAGES_TO_HOLD = 'indy-anoncreds indy-plenum indy-node python3-indy-crypto libindy-crypto'
TMP_DIR = '/tmp/.indy_tmp'


class NodeControlTool:
    MAX_LINE_SIZE = 1024

    def __init__(
            self,
            timeout: int = TIMEOUT,
            backup_format: str = BACKUP_FORMAT,
            test_mode: bool = False,
            deps: List[str] = DEPS,
            backup_target: str = None,
            files_to_preserve: List[str] = None,
            backup_dir: str = None,
            backup_name_prefix: str = None,
            backup_num: int = BACKUP_NUM,
            hold_ext: str = '',
            config=None):
        self.config = config or getConfig()

        assert self.config.UPGRADE_ENTRY, "UPGRADE_ENTRY config parameter must be set"
        self.upgrade_entry = self.config.UPGRADE_ENTRY

        self.test_mode = test_mode
        self.timeout = timeout or TIMEOUT

        config_helper = ConfigHelper(self.config)
        self.backup_dir = backup_dir or config_helper.backup_dir
        self.backup_target = backup_target or config_helper.genesis_dir

        self.tmp_dir = TMP_DIR
        self.backup_format = backup_format
        self.ext_ver = None
        self.deps = deps

        _files_to_preserve = [self.config.lastRunVersionFile, self.config.nextVersionFile,
                              self.config.upgradeLogFile, self.config.lastVersionFilePath,
                              self.config.restartLogFile]

        self.files_to_preserve = files_to_preserve or _files_to_preserve
        self.backup_num = backup_num

        _backup_name_prefix = '{}_backup_'.format(self.config.NETWORK_NAME)

        self.backup_name_prefix = backup_name_prefix or _backup_name_prefix
        self.packages_to_hold = ' '.join([PACKAGES_TO_HOLD, hold_ext])

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

    def _ext_init(self):
        NodeControlUtil.update_package_cache()
        self.ext_ver, ext_deps = self._ext_info()
        self.deps = ext_deps + self.deps
        holds = set([self.upgrade_entry] + ext_deps + self.packages_to_hold.strip(" ").split(" "))
        self.packages_to_hold = ' '.join(list(holds))

    def _ext_info(self, pkg=None):
        pkg_name = pkg or self.upgrade_entry
        return NodeControlUtil.curr_pkt_info(pkg_name)

    def _hold_packages(self):
        if shutil.which("apt-mark"):
            cmd = compose_cmd(['apt-mark', 'hold', self.packages_to_hold])
            ret = NodeControlUtil.run_shell_command(cmd, TIMEOUT)
            if ret.returncode != 0:
                raise Exception('cannot mark {} packages for hold '
                                'since {} returned {}'
                                .format(self.packages_to_hold, cmd, ret.returncode))
            logger.info('Successfully put {} packages on hold'.format(self.packages_to_hold))
        else:
            logger.info('Skipping packages holding')

    def _get_deps_list(self, package):
        logger.info('Getting dependencies for {}'.format(package))
        NodeControlUtil.update_package_cache()
        dep_tree = NodeControlUtil.get_deps_tree(package, self.deps)
        ret = []
        NodeControlUtil.dep_tree_traverse(dep_tree, ret)
        return " ".join(ret)

    def _call_upgrade_script(self, version):
        logger.info('Upgrading indy node to version {}, test_mode {}'.format(version, int(self.test_mode)))

        deps = self._get_deps_list('{}={}'.format(self.upgrade_entry, version))
        deps = '"{}"'.format(deps)

        cmd_file = 'upgrade_indy_node'
        if self.test_mode:
            cmd_file = 'upgrade_indy_node_test'

        cmd = compose_cmd([cmd_file, deps])
        ret = NodeControlUtil.run_shell_script(cmd, self.timeout)
        if ret.returncode != 0:
            raise Exception('upgrade script failed, exit code is {}'.format(ret.returncode))

    def _call_restart_node_script(self):
        logger.info('Restarting indy')
        cmd = compose_cmd(['restart_indy_node'])
        ret = NodeControlUtil.run_shell_script(cmd, self.timeout)
        if ret.returncode != 0:
            raise Exception('restart failed: script returned {}'.format(ret.returncode))

    def _backup_name(self, version):
        return os.path.join(self.backup_dir, '{}{}'.format(
            self.backup_name_prefix, version))

    def _backup_name_ext(self, version):
        return '{}.{}'.format(self._backup_name(version), self.backup_format)

    def _create_backup(self, version):
        logger.debug('Creating backup for {}'.format(version))
        shutil.make_archive(self._backup_name(version),
                            self.backup_format, self.backup_target)

    def _restore_from_backup(self, version):
        logger.info('Restoring from backup for {}'.format(version))
        for file_path in self.files_to_preserve:
            try:
                shutil.copy2(os.path.join(self.backup_target, file_path),
                             os.path.join(self.tmp_dir, file_path))
            except IOError as e:
                logger.warning('Copying {} failed due to {}'
                               .format(file_path, e))
        shutil.unpack_archive(self._backup_name_ext(
            version), self.backup_target, self.backup_format)
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

    def _migrate(self, current_version, new_version):
        migrate(current_version, new_version, self.timeout)

    def _do_migration(self, current_version, new_version):
        try:
            self._create_backup(current_version)
            self._migrate(current_version, new_version)
        except Exception as e:
            self._restore_from_backup(current_version)
            raise e
        self._remove_old_backups()

    def _upgrade(self, new_version, pkg_name, migrate=True, rollback=True):
        self.upgrade_entry = pkg_name
        current_version, _ = self._ext_info()
        try:
            from indy_node.server.upgrader import Upgrader
            node_cur_version = Upgrader.getVersion()
            logger.info('Trying to upgrade from {}={} to {}'.format(pkg_name, current_version, new_version))
            self._call_upgrade_script(new_version)
            if migrate:
                node_new_version = Upgrader.getVersion()
                self._do_migration(node_cur_version, node_new_version)
            self._call_restart_node_script()
        except Exception as ex:
            self._declare_upgrade_failed(from_version=current_version,
                                         to_version=new_version,
                                         reason=str(ex))
            logger.error("Trying to rollback to the previous version {}"
                         .format(ex, current_version))
            if rollback:
                self._upgrade(current_version, pkg_name, rollback=False)

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
                new_version = command['version']
                pkg_name = command['pkg_name']
                self._upgrade(new_version, pkg_name)
            elif command[MESSAGE_TYPE] == RESTART_MESSAGE:
                self._restart()
        except json.decoder.JSONDecodeError as e:
            logger.error("JSON decoding failed: {}".format(e))
        except Exception as e:
            logger.error("Unexpected error in process_data {}".format(e))

    def _declare_upgrade_failed(self, *,
                                from_version,
                                to_version,
                                reason):
        msg = 'Upgrade from {from_version} to {to_version} failed: {reason}'\
              .format(from_version=from_version,
                      to_version=to_version,
                      reason=reason)
        logger.error(msg)

    def start(self):
        self._ext_init()
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
