#!/bin/bash -xe

if [ "$1" = "--help" ] ; then
  echo "Usage: $0 <path-to-repo-folder> <release-version-dotted>"
fi

repo="$1"
version_dotted="$2"

METADATA_FNAME="__metadata__.py"
MANIFEST_FNAME="manifest.txt"

echo -e "\n\nAbout to start updating package $repo to version $version_dotted info from cur dir: $(pwd)"

metadata="$(find $repo -name $METADATA_FNAME)"

if [ -z $metadata ] ; then
  echo "FAILED finding metadata"
  exit $ret
fi

version=$(sed -r "s/\./, /g" <<< $version_dotted)

echo -e "\n\nUpdating version in $metadata with $version"
sed -i -r "s~(__version_info__ = \()[0-9, ]+~\1$version~" "$metadata"
ret=$?
if [ $ret -ne 0 ] ; then
  echo "FAILED ret: $ret"
  exit $ret
fi

echo -e "\n\nReplace postfixes"
sed -i -r "s~indy-node-[a-z]+~indy-node~" "$repo/setup.py"
sed -i -r "s~indy-plenum-[a-z]+~indy-plenum~" "$repo/setup.py"
sed -i -r "s~indy-anoncreds-[a-z]+~indy-anoncreds~" "$repo/setup.py"

echo -e "Adapt the dependencies for the Canonical archive"
sed -i "s~python-dateutil~python3-dateutil~" "$repo/setup.py"
sed -i "s~timeout-decorator~python3-timeout-decorator~" "$repo/setup.py"

# create manifest file
repourl=$(git --git-dir $repo/.git --work-tree $repo config --get remote.origin.url)
hashcommit=$(git --git-dir $repo/.git --work-tree $repo rev-parse HEAD)
manifest="// built from: repo version hash\n$repourl $version_dotted $hashcommit"
manifest_file=$(echo $metadata | sed -r "s/${METADATA_FNAME}$/${MANIFEST_FNAME}/")

echo "Adding manifest\n=======\n$manifest\n=======\n into $manifest_file"
rm -rf $manifest_file
echo -e $manifest >$manifest_file

echo -e "Finished preparing $repo for publishing\n"
