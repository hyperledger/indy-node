#!/usr/bin/python3.5
import sys
import traceback

from stp_core.common.log import getlogger

logger = getlogger()

ENV_FILE_PATH = "/etc/indy/indy.env"

node_ip_key = 'NODE_IP'
client_ip_key = 'NODE_CLIENT_IP'


def are_ips_present_in_env():
    node_ip_present = False
    client_ip_present = False

    with open(ENV_FILE_PATH, "r") as fenv:
        for line in fenv.readlines():
            key = line.split('=')[0].strip()
            if key == node_ip_key:
                node_ip_present = True
                logger.info("Node IP is present in '{}': {}".format(ENV_FILE_PATH, line.strip()))
            elif key == client_ip_key:
                client_ip_present = True
                logger.info("Client IP is present in '{}': {}".format(ENV_FILE_PATH, line.strip()))
    return node_ip_present, client_ip_present


def append_ips_to_env(node_ip, client_ip):
    node_ip_key = 'NODE_IP'
    client_ip_key = 'NODE_CLIENT_IP'

    if node_ip is None and client_ip is None:
        return

    with open(ENV_FILE_PATH, "a") as fenv:
        fenv.write("\n")
        if node_ip is not None:
            line = node_ip_key + "=" + node_ip
            logger.info("Appending line to '{}': {}".format(ENV_FILE_PATH, line))
            fenv.write("{}\n".format(line))
        if client_ip is not None:
            line = client_ip_key + "=" + client_ip
            logger.info("Appending line to '{}': {}".format(ENV_FILE_PATH, line))
            fenv.write("{}\n".format(line))


def migrate_all():
    node_ip = None
    client_ip = None
    node_ip_present, client_ip_present = are_ips_present_in_env()

    if not node_ip_present:
        node_ip = "0.0.0.0"

    if not client_ip_present:
        client_ip = "0.0.0.0"

    if node_ip is not None or client_ip is not None:
        try:
            append_ips_to_env(node_ip, client_ip)
        except Exception:
            logger.error(traceback.print_exc())
            logger.error("Could not append node and client IPs to indy env file")
            return False
    else:
        logger.info("No modification of env file is needed")

    return True


if migrate_all():
    logger.info("Node/client IPs migration complete")
else:
    logger.error("Node/client IPs migration failed.")
    sys.exit(1)
