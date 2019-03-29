#!/bin/bash

set -e

usage_str="Usage: $0"

if [ "$1" = "--help" ] ; then
  echo $usage_str
  exit 0
fi

repourl=$(git config --get remote.origin.url)
hashcommit=$(git $repo rev-parse HEAD)

python3 -c "import indy_node; indy_node.set_manifest({'repo': '$repourl', 'sha1': '$hashcommit', 'version': indy_node.__version__})"
