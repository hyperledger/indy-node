#   Copyright 2017 Sovrin Foundation
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#

#!/bin/bash -x

deps="$1"
if [ -z "$deps" ] ; then
  exit 1
fi

echo "Try to donwload indy version $deps"
apt-get -y update && apt-get --download-only -y --allow-downgrades --allow-change-held-packages install $deps
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Failed to obtain $deps"
  exit 1
fi

echo "Stop indy-node"
systemctl stop indy-node

echo "Run indy upgrade to $deps"
apt-get -y --allow-downgrades --allow-change-held-packages --reinstall install $deps
ret=$?
if [ $ret -ne 0 ] ; then
  echo "Upgrade to $deps failed"
fi
