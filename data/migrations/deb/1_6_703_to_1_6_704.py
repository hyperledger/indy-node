#!/usr/bin/python3.5

from indy_common.migration.helper import update_indy_env

from stp_core.common.log import getlogger

logger = getlogger()

CLIENT_CONNECTIONS_LIMIT_KEY = "CLIENT_CONNECTIONS_LIMIT"
CLIENT_CONNECTIONS_LIMIT_VAL = 500


logger.info("Going to update clients connections limit.")
update_indy_env(CLIENT_CONNECTIONS_LIMIT_KEY, CLIENT_CONNECTIONS_LIMIT_VAL)
logger.info("Done.")
