#!/bin/bash -x

if [ "$1" = "--help" ] ; then
  echo "Usage: $0 <path-to-repo-folder> <patch-version>"
fi

repo="$1"
patch="$2"

metadata=$(find $repo -name __metadata__.py)

if [ -z $metadata ] ; then
  echo "FAILED finding metadata"
  exit $ret
fi
version=$(grep __version_info__ $metadata)
version=$(sed -r "s/.*__version_info__ = \(([0-9, ]+)\).*/\1/" <<< $version)
version=$(sed -r "s/,\s/./g" <<< $version)
version="$version.$patch"
echo "$version"
