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

echo "Installing indy-node..."
pushd indy-node
pip install -e .[tests]
popd
echo "Installed indy-node..."

echo "Installing indy-plenum..."
pushd indy-plenum
pip uninstall -y indy-plenum
pip install -e .[tests]
popd
echo "Installed indy-plenum..."

echo "Installing flake8..."
pip install flake8
echo "Installed flake8"


echo "Indy-node and indy-plenum are ready for being used"
