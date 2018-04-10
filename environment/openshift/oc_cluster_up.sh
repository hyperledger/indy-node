#!/bin/bash

# ==============================================================================
# Script for setting up an OpenShift cluter in Docker for Windows
#
# * Requires the OpenShift Origin CLI
# ------------------------------------------------------------------------------
#
# Usage on WIndows:
#  
# MSYS_NO_PATHCONV=1 ./oc_cluster_up.sh
#
# ==============================================================================

oc cluster up --metrics=true --host-data-dir=/var/lib/origin/data --use-existing-config