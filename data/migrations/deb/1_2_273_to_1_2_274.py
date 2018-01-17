#!/usr/bin/python3.5

from stp_core.common.log import getlogger

logger = getlogger()

ENV_FILE_PATH = "/etc/indy/indy.env"
CLIENT_CONNECTIONS_LIMIT = 15360


def migrate_env():
    line = "CLIENT_CONNECTIONS_LIMIT={}".format(CLIENT_CONNECTIONS_LIMIT)
    with open(ENV_FILE_PATH, "a") as envfile:
        logger.info("Append '{}' line to '{}'."
                    .format(line, ENV_FILE_PATH))
        envfile.write("\n" + line)


migrate_env()
