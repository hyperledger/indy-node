#!/bin/bash -x

if [ "$1" = "--help" ] ; then
  echo "Usage: $0 <path-to-repo-folder> <patch-version>"
fi

repo="$1" 
patch="$2"

echo -e "\n\nAbout to start updating package $repo tp patch version $patch info from cur dir: $(pwd)"

metadata="$(find $repo -name __metadata__.py)"

if [ -z $metadata ] ; then
  echo "FAILED finding metadata"
  exit $ret
fi

script_dir=$(dirname $0)
version=$("${script_dir}/get-package-version.sh" "$repo" "$patch")
version=$(sed -r "s/\./, /g" <<< $version)

echo -e "\n\nUpdating version in $metadata with $version"
sed -i -r "s/(__version_info__ = \()[0-9, ]+/\1$version/" "$metadata"
ret=$?
if [ $ret -ne 0 ] ; then
  echo "FAILED ret: $ret"
  exit $ret
fi

echo -e "Finished preparing $repo for publishing\n"
