import os
import shutil

from stp_core.common.log import getlogger

logger = getlogger()

ENV_FILE_PATH = "/etc/indy/indy.env"


def update_indy_env(key, val):
    key_found = False

    ENV_FILE_PATH_TMP = ENV_FILE_PATH + "_tmp"
    logger.info("Make a copy '{}' of an original env file '{}'."
                .format(ENV_FILE_PATH_TMP, ENV_FILE_PATH))
    # Make a copy to inherit r/w/own flags.
    shutil.copy(ENV_FILE_PATH, ENV_FILE_PATH_TMP)

    new_line = "{}={}\n".format(key, val)

    with open(ENV_FILE_PATH, "r") as old_env_file:
        with open(ENV_FILE_PATH_TMP, "w") as new_env_file:
            for line in old_env_file.readlines():
                _key = line.split('=')[0].strip()
                if key == _key:
                    key_found = True
                    line = new_line
                logger.info("Write '{}' line to '{}'.".format(line.strip(), ENV_FILE_PATH_TMP))
                new_env_file.write(line)

    if not key_found:
        logger.info("Key '{}' is not found in '{}', append line."
                    .format(key, ENV_FILE_PATH))
        with open(ENV_FILE_PATH, "a") as env_file:
            env_file.write("\n" + new_line)
        logger.info("Remove unnecessary '{}'.".format(ENV_FILE_PATH_TMP))
        os.remove(ENV_FILE_PATH_TMP)
    else:
        logger.info("Rename '{}' to '{}'.".format(ENV_FILE_PATH_TMP, ENV_FILE_PATH))
        shutil.move(ENV_FILE_PATH_TMP, ENV_FILE_PATH)
