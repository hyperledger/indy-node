#!/usr/bin/python3.5
import os

from stp_core.common.log import getlogger
from indy_common.config_util import getConfig

import indy_node.general_config.indy_config as indy_config


def migrate():
    config = getConfig()
    logger = getlogger()

    general_config_path = os.path.join(config.GENERAL_CONFIG_DIR, config.GENERAL_CONFIG_FILE)

    if os.path.exists(general_config_path):
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


migrate()
