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
#! /bin/bash

set -e

PARALLELISM_FACTOR=${1:-1}
REQ_NUM=${2:-1}
REQ_TYPE=${3:ATTR}
CLIENT_LIST=${4:-load_test_clients\.list}

TIMEOUT=0
time_stamp=$(date +%Y_%m_%d_%H_%M_%S)
printf -v OUT_DIR 'test_result_%s_%s__%s' "$PARALLELISM_FACTOR" "$REQ_NUM" "$time_stamp"

mkdir -p $OUT_DIR
echo "starting $PARALLELISM_FACTOR clients, making them send $REQ_NUM requests"
for I in $(seq 1 $(($PARALLELISM_FACTOR)));
  do
  echo "starting client #$I"
    python -u scripts/load_test.py -t $REQ_TYPE -r $REQ_NUM --clients-list="$CLIENT_LIST" --skip-clients $I --timeout $TIMEOUT &> "$OUT_DIR/$I.log"  &
  done
