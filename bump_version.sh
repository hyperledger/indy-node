#!/bin/bash

set -e

usage_str="Usage: $0 <version-dotted>"

if [ -z "$1" ] ; then
    echo $usage_str
    exit 1
fi

if [ "$1" = "--help" ] ; then
  echo $usage_str
  exit 0
fi

python3 -c "import indy_node; indy_node.set_version('$1')"
