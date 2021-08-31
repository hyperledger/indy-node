#!/bin/bash -xe

if [ "$1" = "--help" ] ; then
  echo "Usage: $0 <path-to-repo-folder> <main-module-name> <release-version-dotted> <distro-packages>"
  echo "<distro-packages> - Set to 'debian-packages' when preparing deb packages, and 'python-packages' when preparing PyPi packages."
  exit 0
fi

repo="$1"
module_name="$2"
version_dotted="$3"
distro_packages="$4"

BUMP_SH_SCRIPT="bump_version.sh"
GENERATE_MANIFEST_SCRIPT="generate_manifest.sh"

pushd $repo

echo -e "\nSetting version to $version_dotted"
bash -ex $BUMP_SH_SCRIPT $version_dotted
cat $module_name/__version__.json

echo -e "\nGenerating manifest"
bash -ex $GENERATE_MANIFEST_SCRIPT
cat $module_name/__manifest__.json

echo -e "\n\nPrepares indy-node debian package version"
sed -i -r "s~indy-node==([0-9\.]+[0-9])(\.)?([a-z]+)~indy-node==\1\~\3~" setup.py

if [ "$distro_packages" = "debian-packages" ]; then
  # Only used for the deb package builds, NOT for the PyPi package builds.
  # Update the package names to match the versions that are pre-installed on the os.
  echo -e "\nAdapt the dependencies for the Canonical archive"
  #### ToDo adjust packages for the Cannonical archive for Ubuntu 20.04 (focal)
  # sed -i "s~timeout-decorator~python3-timeout-decorator~" setup.py
  # sed -i "s~distro~python3-distro~" setup.py
elif [ "$distro_packages" = "python-packages" ]; then
  echo -e "\nNo adaption of dependencies for python packages"
else
  echo -e "\nNo distribution specified. Please, specify distribution as 'debian-packages' or 'python-packages'."
  exit 1
fi

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

