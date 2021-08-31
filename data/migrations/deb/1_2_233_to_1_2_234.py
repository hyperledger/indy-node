#!/usr/bin/python3.5
import os
import shutil
import pwd
import grp
import stat

from stp_core.common.log import getlogger
from indy_common.config_util import getConfigOnce
from indy_common.config_helper import ConfigHelper

import indy_node.general_config.indy_config as indy_config


logger = getlogger()


def ext_copytree(src, dst):
    if not os.path.isdir(dst):
        shutil.copytree(src, dst)


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


def migrate_nodes_data():
    config = getConfigOnce()
    config_helper = ConfigHelper(config)

    # Move data
    old_nodes_data_dir = os.path.join(config_helper.ledger_data_dir, 'nodes')
    new_node_data_dir = config_helper.ledger_data_dir
    try:
        visit_dirs = os.listdir(old_nodes_data_dir)
    except FileNotFoundError:
        visit_dirs = []
    for node_name in visit_dirs:
        move_path = os.path.join(old_nodes_data_dir, node_name)
        to_path = os.path.join(new_node_data_dir, node_name)
        ext_copytree(move_path, to_path)
    shutil.rmtree(old_nodes_data_dir)
    set_own_perm("indy", [new_node_data_dir])


def migrate_config():
    config = getConfigOnce()
    general_config_path = os.path.join(config.GENERAL_CONFIG_DIR, config.GENERAL_CONFIG_FILE)

    if not os.path.exists(general_config_path):
        return

    if not os.path.isfile(general_config_path):
        logger.error("General config '{}' exists, but it is not a regular file, abort migration."
                     .format(general_config_path))
    else:
        logger.info("Open '{}' for appending missing paths configuration."
                    .format(general_config_path))
        general_config_file = open(general_config_path, "a")
        logger.info("Open '{}' to get missing paths configuration."
                    .format(indy_config.__file__))
        indy_config_file = open(indy_config.__file__, "r")

        general_config_file.write("\n")

        for line in indy_config_file:
            if not line.startswith("NETWORK_NAME") and not line == "# Current network\n":
                logger.info("Append '{}' line to '{}'."
                            .format(line, general_config_path))
                general_config_file.write(line)

        general_config_file.close()
        indy_config_file.close()


def migrate_all():
    # Migrate config first!
    migrate_config()
    migrate_nodes_data()


migrate_all()
