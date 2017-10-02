#!/bin/bash -x

# This script is intended to be used by rebranding upgrade

systemctl start atd
at -f /usr/local/bin/complete_rebranding_upgrade now
