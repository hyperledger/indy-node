#!/bin/bash -e
set -e
set -x

USERNAME="$1"
USERHOME=$(eval echo "~$USERNAME")
VENVDIR="$USERHOME/$2"

PY_GLOBAL="/usr/local/lib/python3.5/dist-packages"
PY_USER="$VENVDIR/lib/python3.5/site-packages"

apt-get update
apt-get install -y python3-charm-crypto

su -c "cp -r $PY_GLOBAL/Charm_Crypto-0.0.0.egg-info $PY_USER" - $USERNAME
su -c "cp -r $PY_GLOBAL/charm $PY_USER" - $USERNAME
