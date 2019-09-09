#!/bin/bash -xe

if [ "$1" = "--help" ] ; then
  echo "Usage: $0 <path-to-repo-folder> <release-version-dotted>"
  exit 0
fi

repo="$1"
version_dotted="$2"

pushd $repo

echo -e "\nSetting version to $version_dotted"
bash -ex ./bump_version.sh $version_dotted
cat indy_node/__version__.json

echo -e "\nGenerating manifest"
bash -ex ./generate_manifest.sh
cat indy_node/__manifest__.json

echo -e "\n\nPrepares indy-plenum debian package version"
sed -i -r "s~indy-plenum==([0-9\.]+[0-9])(\.)?([a-z]+)~indy-plenum==\1\~\3~" setup.py

echo -e "\nAdapt the dependencies for the Canonical archive"
sed -i "s~timeout-decorator~python3-timeout-decorator~" setup.py
sed -i "s~distro~python3-distro~" setup.py

echo "Preparing config files"
GENERAL_CONFIG_DIR="\/etc\/indy"
REPO_GENERAL_CONFIG_DIR="indy_node/general_config"
# Define user config directory
sed -i "s/^\(GENERAL_CONFIG_DIR\s*=\s*\).*\$/\1\"$GENERAL_CONFIG_DIR\"/" indy_common/config.py
# Create user config
cp $REPO_GENERAL_CONFIG_DIR/general_config.py $REPO_GENERAL_CONFIG_DIR/indy_config.py
cat $REPO_GENERAL_CONFIG_DIR/ubuntu_platform_config.py >> $REPO_GENERAL_CONFIG_DIR/indy_config.py
rm -f $REPO_GENERAL_CONFIG_DIR/general_config.py
rm -f $REPO_GENERAL_CONFIG_DIR/ubuntu_platform_config.py
rm -f $REPO_GENERAL_CONFIG_DIR/windows_platform_config.py

popd

echo -e "\nFinished preparing $repo for publishing\n"
