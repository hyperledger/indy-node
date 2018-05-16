#!/bin/bash -x

if [ "$INDY_CONTROL" = "" ]; then

  # Upgrade may change service files
  systemctl daemon-reload
  systemctl reset-failed

  echo "Starting indy-node"
  systemctl start indy-node

  echo "Restarting agent"
  systemctl restart indy-node-control

elif [ "$INDY_CONTROL" = "supervisorctl" ]; then

  # Upgrade may change service files
  supervisorctl reread
  supervisorctl update

  echo "Starting indy-node"
  supervisorctl start indy-node

  echo "Restarting agent"
  supervisorctl restart indy-node-control

else

  echo "Invalid setting for 'INDY_CONTROL' environment variable: $INDY_CONTROL"
  exit 1

fi
