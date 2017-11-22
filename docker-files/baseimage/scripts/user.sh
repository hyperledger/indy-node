#!/bin/bash
set -e
set -x

USERID="$1"
USERNAME="$2"

useradd -ms /bin/bash -u "$USERID" "$USERNAME"

USERHOME=$(eval echo "~$USERNAME")
VENVNAME="$USERHOME/$3"
su -c "virtualenv -p python3.5 $VENVNAME" - "$USERNAME"

# need virtualenv activation for different shells
# (intractive/non-interactive login and non-login)
echo "source $VENVNAME/bin/activate" | tee -a "$USERHOME"/{.bashrc,.profile} >/dev/null
