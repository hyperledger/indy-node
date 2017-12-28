#!/bin/bash
set -e
set -x

apt-get -y autoremove
rm -rf /var/lib/apt/lists/*
