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

#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Please specify GitHib user name get a fork from and virtualenv name"
    exit 1
fi

fork_name=$1
virtualenv_name=$2

echo "Cloning indy-plenum and indy-node..."
git clone https://github.com/${fork_name}/indy-plenum
git clone https://github.com/${fork_name}/indy-node
echo "Cloned indy-plenum and indy-node"

echo "Creating virtual environment..."
source /usr/local/bin/virtualenvwrapper.sh
mkvirtualenv -p python3.5 ${virtualenv_name}
workon ${virtualenv_name}
echo "Created virtual environment"

echo "Installing Charm Crypto..."
cp -r /usr/local/lib/python3.5/dist-packages/Charm_Crypto-0.0.0.egg-info ~/.virtualenvs/${virtualenv_name}/lib/python3.5/site-packages/Charm_Crypto-0.0.0.egg-info
cp -r /usr/local/lib/python3.5/dist-packages/charm ~/.virtualenvs/${virtualenv_name}/lib/python3.5/site-packages/charm
echo "Installed Charm Crypto..."

echo "Installing indy-node..."
pushd indy-node
pip install -e .
popd
echo "Installed indy-node..."

echo "Installing indy-plenum..."
pushd indy-plenum
pip uninstall -y indy-plenum-dev
pip install -e .
popd
echo "Installed indy-plenum..."

echo "Installing pytest..."
pip install pytest pytest-asyncio pytest-xdist
echo "Installed pytest"

echo "Installing flake8..."
pip install flake8
echo "Installed flake8"


echo "Indy-node and indy-plenum are ready for being used"
