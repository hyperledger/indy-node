#!/bin/bash

package="$1"
if [ -z "$package" ] ; then
  exit 1
fi

SCRIPT_DIR=$(dirname $0)
TARGET_PACKAGES=("indy-plenum" "indy-anoncreds")

res=""
for item in "${TARGET_PACKAGES[@]}"
do
	info=$(apt-cache show $package | grep 'Depends')
	if [[ $info == *"${item}"* ]]; then
		info=$(echo "$info" | sed -r "s/.*${item} \(= ([0-9]+\.[0-9]+\.[0-9]+)\).*/${item}=\1/")
		info=$($SCRIPT_DIR/get_package_dependencies_ubuntu.sh $info)
		res="${info} ${res}"
	fi
done

if [[ -z "$res" ]]; then
	res="${res} "
fi

echo "${res}${package}"

