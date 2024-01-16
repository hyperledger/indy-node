#!/bin/sh

# checks that this script didn't run manually
me=`basename "$0"`
if [ "$me" = ".common.sh" ];then
  echo >&2 "This script is not expected to be run separately."
  exit 1
fi

# checks docker installed
hash docker 2>/dev/null || {
  echo >&2 "This script requires Docker but it's not installed."
  echo >&2 "Refer to documentation to fulfill requirements."
  exit 1
}

# checks docker compose installed
docker compose version &>/dev/null
if [ "$?" -eq "1" ];then
  echo >&2 "This script requires Docker compose but it's not installed."
  echo >&2 "Refer to documentation to fulfill requirements."
  exit 1
fi

# checks docker daemon running
docker info &>/dev/null
if [ "$?" -eq "1" ];then
  echo >&2 "This script requires Docker daemon to run. Start Docker and try again."
  echo >&2 "Refer to documentation to fulfill requirements."
  exit 1
fi

# We use "SI" measures here because the measurement in the UI and actual bytes
# do not align exactly
NORMAL_MINIMUM=$(( 4 * 1000 * 1000 * 1000 ))
dockermem=$(docker info --format '{{.MemTotal}}')

# dockermem must be >= minimum
if [ $dockermem -lt $NORMAL_MINIMUM ]; then
  echo >&2 "This script requires that docker has at least 4GB of memory available."
  echo >&2 "Refer to documentation to fulfill requirements."
  exit 1
fi

# when running network lock_file must not exist
if [ "${NO_LOCK_REQUIRED}" = "true" ];then
  if [ -f ${LOCK_FILE} ];then
    echo "Network already in use (${LOCK_FILE} present)." >&2
    echo "Restart with ./resume.sh or remove with ./remove.sh before running again." >&2
    exit 1
  fi
else
  composeFile=""
  if [ -f ${LOCK_FILE} ]; then
    #read the first line of the lock file and store the value as it's the compose file option
    composeFile=`sed '1q;d' ${LOCK_FILE}`
  else
    echo "Network is not running (${LOCK_FILE} not present)." >&2
    echo "Run it with ./run.sh first" >&2
    exit 1
  fi
fi

current_dir=${PWD##*/}

