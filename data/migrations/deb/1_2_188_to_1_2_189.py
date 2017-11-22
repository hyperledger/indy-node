#!/usr/bin/python3.5
import pwd
import grp
import os
import stat
import shutil
from importlib.util import module_from_spec, spec_from_file_location

from stp_core.common.log import getlogger

baseDir = '/var/lib/indy'
GENERAL_CONFIG_DIR = '/etc/indy'
GENERAL_CONFIG_FILE = 'indy_config.py'
LOG_DIR = '/var/log/indy'
NODE_BASE_DATA_DIR = baseDir
CLI_BASE_DIR = '/home/indy/.indy-cli'
CLI_NETWORK_DIR = '/home/indy/.indy-cli/networks'

logger = getlogger()

old_base_dir = '/home/indy/.indy'


def ext_copytree(src, dst):
    if not os.path.isdir(dst):
        shutil.copytree(src, dst)


def migrate_genesis_txn(old_base_txn_dir, new_base_txn_dir, new_cli_net_base_dir):
    logger.info('Move genesis transactions {} -> {}'.format(old_base_txn_dir, new_base_txn_dir))
    for suffix in ('sandbox', 'live', 'local'):
        new_txn_dir = os.path.join(new_base_txn_dir, suffix)
        new_cli_network_dir = os.path.join(new_cli_net_base_dir, suffix)
        os.makedirs(new_txn_dir, exist_ok=True)
        os.makedirs(new_cli_network_dir, exist_ok=True)

        old_domain_genesis = os.path.join(old_base_txn_dir, 'domain_transactions_{}_genesis'.format(suffix))
        old_pool_genesis = os.path.join(old_base_txn_dir, 'pool_transactions_{}_genesis'.format(suffix))
        new_domain_genesis = os.path.join(new_txn_dir, 'domain_transactions_genesis')
        new_pool_genesis = os.path.join(new_txn_dir, 'pool_transactions_genesis')
        new_cli_domain_genesis = os.path.join(new_cli_network_dir, 'domain_transactions_genesis')
        new_cli_pool_genesis = os.path.join(new_cli_network_dir, 'pool_transactions_genesis')

        if os.path.exists(old_domain_genesis):
            shutil.copy2(old_domain_genesis, new_domain_genesis)
            shutil.copy2(old_domain_genesis, new_cli_domain_genesis)
        if os.path.exists(old_pool_genesis):
            shutil.copy2(old_pool_genesis, new_pool_genesis)
            shutil.copy2(old_pool_genesis, new_cli_pool_genesis)

    logger.info('done')


def _get_network_from_txn_file_name(file_name: str):
    name_split = file_name.split("_")
    ret_name = "sandbox"
    if name_split and name_split[-1] in ["live", "local", "sandbox"]:
        ret_name = name_split[-1]
    return ret_name


def get_network_name():
    network_name = 'sandbox'
    old_general_config = os.path.join(old_base_dir, 'indy_config.py')
    spec = spec_from_file_location('old_general_config', old_general_config)
    old_cfg = module_from_spec(spec)
    spec.loader.exec_module(old_cfg)
    if hasattr(old_cfg, 'poolTransactionsFile'):
        network_name = _get_network_from_txn_file_name(old_cfg.poolTransactionsFile)
    elif hasattr(old_cfg, 'domainTransactionsFile'):
        network_name = _get_network_from_txn_file_name(old_cfg.domainTransactionsFile)
    elif hasattr(old_cfg, 'current_env') and old_cfg.current_env != 'test':
        network_name = old_cfg.current_env
    return network_name


def migrate_general_config(old_general_config, new_general_config, network_name):
    logger.info('Migrate general config file {} -> {} for network {}'.format(
        old_general_config, new_general_config, network_name))

    f = open(old_general_config, "r")
    lines = f.readlines()
    f.close()

    f = open(new_general_config, "a+")
    f.write("\n")
    for line in lines:
        if not line.startswith('current_env') and not line.startswith('poolTransactionsFile') and\
                not line.startswith('domainTransactionsFile'):
            f.write(line)
    line = "NETWORK_NAME = '{}'\n".format(network_name)
    f.write(line)
    f.close()
    # os.remove(old_general_config)


def remove_network_from_dir_name(root_dir):
    try:
        visit_dirs = os.listdir(root_dir)
    except FileNotFoundError:
        visit_dirs = []
    for dname in visit_dirs:
        _dname = dname
        _dname = _dname.replace("_sandbox", "")
        _dname = _dname.replace("_live", "")
        _dname = _dname.replace("_local", "")
        if _dname != dname:
            os.rename(os.path.join(root_dir, dname), os.path.join(root_dir, _dname))
        if _dname in ['pool_state', 'domain_state', 'config_state', 'idr_cache_db']:
            shutil.rmtree(os.path.join(root_dir, _dname))


def set_own_perm(usr, dir_list):
    uid = pwd.getpwnam(usr).pw_uid
    gid = grp.getgrnam(usr).gr_gid
    perm_mask_rw = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP
    perm_mask_rwx = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP

    for cdir in dir_list:
        os.chown(cdir, uid, gid)
        os.chmod(cdir, perm_mask_rwx)
        for croot, sub_dirs, cfiles in os.walk(cdir):
            for fs_name in sub_dirs:
                os.chown(os.path.join(croot, fs_name), uid, gid)
                os.chmod(os.path.join(croot, fs_name), perm_mask_rwx)
            for fs_name in cfiles:
                os.chown(os.path.join(croot, fs_name), uid, gid)
                os.chmod(os.path.join(croot, fs_name), perm_mask_rw)


def migrate_all():
    # Check which network name should we use
    network_name = get_network_name()
    logger.info('Network name is {}'.format(network_name))
    base_dir = baseDir

    logger.info('Start migration of directories/files.')

    # Migrate general config file
    old_general_config = os.path.join(old_base_dir, 'indy_config.py')
    new_general_config = os.path.join(GENERAL_CONFIG_DIR, GENERAL_CONFIG_FILE)
    os.makedirs(GENERAL_CONFIG_DIR, exist_ok=True)
    migrate_general_config(old_general_config, new_general_config, network_name)
    old_srv_cfg = os.path.join(old_base_dir, 'indy.env')
    new_srv_cfg = os.path.join(GENERAL_CONFIG_DIR, 'indy.env')
    shutil.copy2(old_srv_cfg, new_srv_cfg)

    # Create indy cli folder
    os.makedirs(CLI_NETWORK_DIR, exist_ok=True)

    # Move genesis transactions
    migrate_genesis_txn(old_base_dir, NODE_BASE_DATA_DIR, CLI_NETWORK_DIR)

    # Move data
    old_nodes_data_dir = os.path.join(old_base_dir, 'data', 'nodes')
    new_node_data_dir = os.path.join(NODE_BASE_DATA_DIR, network_name, 'data', 'nodes')
    try:
        visit_dirs = os.listdir(old_nodes_data_dir)
    except FileNotFoundError:
        visit_dirs = []
    for node_name in visit_dirs:
        move_path = os.path.join(old_nodes_data_dir, node_name)
        to_path = os.path.join(new_node_data_dir, node_name)
        ext_copytree(move_path, to_path)
        remove_network_from_dir_name(to_path)
    # shutil.rmtree(os.path.join(old_base_dir, 'data', 'nodes'))

    # Move *_info* files and logs; delete system __pycache__; move key folder
    new_log_dir = os.path.join(LOG_DIR, network_name)
    os.makedirs(new_log_dir, exist_ok=True)
    new_key_dir = os.path.join(base_dir, network_name, 'keys')
    os.makedirs(new_key_dir, exist_ok=True)
    try:
        visit_dirs = os.listdir(old_base_dir)
    except FileNotFoundError:
        visit_dirs = []
    for fs_name in visit_dirs:
        full_path = os.path.join(old_base_dir, fs_name)
        if "_info" in fs_name:
            shutil.copy2(full_path, os.path.join(base_dir, network_name))
        elif ".log" in fs_name:
            shutil.copy2(full_path, new_log_dir)
        elif os.path.isdir(full_path) and fs_name not in ['data', '__pycache__', 'wallets', 'sample', 'plugins']:
            ext_copytree(full_path, os.path.join(new_key_dir, fs_name))

    # Remove old dir
    # os.removedirs(old_base_dir)

    logger.info('Finish migration of directories/files.')


if not os.path.exists(old_base_dir):
    msg = 'Can not find old base directory \'{}\'. Nothing to migrate.'.format(old_base_dir)
    logger.warning(msg)


migrate_all()
set_own_perm("indy", ["/etc/indy", "/var/lib/indy", "/var/log/indy", "/home/indy/.indy-cli"])
