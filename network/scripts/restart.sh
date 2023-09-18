#!/bin/bash

./$(dirname "$0")/stop.sh
echo "Waiting 30s for containers to stop"
sleep 30
./$(dirname "$0")/resume.sh
