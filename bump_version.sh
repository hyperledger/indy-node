#!/bin/bash -e

usage_str="Usage: $0 <release-version-dotted>"

if [ -z "$1" ] ; then
    echo $usage_str
    exit 0
fi

if [ "$1" = "--help" ] ; then
  echo $usage_str
  exit 0
fi

dotted_version=$1

import_metadata_str="indy_node.__metadata__"

# call python set_version function

python3 -c "from $import_metadata_str import set_version, split_version_from_str
set_version(split_version_from_str(\"$dotted_version\"))"
