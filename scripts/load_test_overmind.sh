#! /bin/bash

set -e

PARALLELISM_FACTOR=${1:-1}
REQ_NUM=${2:-1}

TIMEOUT=0
time_stamp=$(date +%Y_%m_%d_%H_%M_%S)
printf -v OUT_DIR 'test_result_%s_%s__%s' "$PARALLELISM_FACTOR" "$REQ_NUM" "$time_stamp"

mkdir -p $OUT_DIR
echo "starting $PARALLELISM_FACTOR clients, making them send $REQ_NUM requests"
for I in $(seq 0 $(($PARALLELISM_FACTOR - 1)));
  do
  echo "starting client #$I"
    python -u gen_load_ratcheting -r $REQ_NUM --skip-clients $I --timeout $TIMEOUT &> "$OUT_DIR/$I.log" &
  done