#!/bin/bash
set -e
set -x

USERID="$1"
USERNAME="$2"

useradd -ms /bin/bash -u "$USERID" "$USERNAME"

USERHOME=$(eval echo "~$USERNAME")
VENVPATH="$USERHOME/$3"
su -c "virtualenv -p python3.5 \"$VENVPATH\"" - "$USERNAME"

# TODO virtualenv activation seems as better approach
# but it's more tricky (failed to find out how) to automate
# that for all cases (e.g. non interactive docker run/exec)
USER_PYTHON=$(su -c "which python" - "$USERNAME")
USER_PIP=$(su -c "which pip" - "$USERNAME")

ln -sf "${VENVPATH}/bin/python" "$USER_PYTHON"
ln -sf "${VENVPATH}/bin/pip" "$USER_PIP"
