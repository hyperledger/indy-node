#!/bin/bash -e
set -e
set -x

USERNAME="$1"

apt-get update
apt-get install -y libindy
