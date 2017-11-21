#!/bin/bash
set -e
set -x

USERID="$1"
USERNAME="$2"

useradd -ms /bin/bash -u "$USERID" "$USERNAME"

USERHOME=$(eval echo "~$USERNAME")
VENVNAME="$USERHOME/$3"
su "$USERNAME" - -c "virtualenv -p python3.5 $VENVNAME"
echo "source $VENVNAME/bin/activate" >>"$USERHOME/.bashrc"
