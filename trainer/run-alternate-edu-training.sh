#!/bin/bash
# Copyright 2016 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# This sample assumes you're already setup for using CloudML.  If this is your
# first time with the service, start here:
# https://cloud.google.com/ml/docs/how-tos/getting-set-up

# Expects the following env:
# export FULL_PROJECT=$(gcloud config list project --format "value(core.project)")
# export PROJECT="$(echo $FULL_PROJECT | cut -f2 -d ':')"
# export REGION='us-central1' #OPTIONALLY CHANGE THIS
# export MODEL_NAME=equipmentparts
# export MODEL_VERSION="${MODEL_NAME}_1_$(date +%s)"
# 

# This variation is for use in workshops where there is limited time to
# run the full preprocessing.
#
declare -r PROJECT=$(gcloud config list project --format "value(core.project)")

declare -r BUCKET="gs://iot-ml-edge-public"
declare -r GCS_PATH="${BUCKET}"
declare -r DICT_FILE=${GCS_PATH}/parts_images_dictionary.txt

# declare -r MODEL_NAME=lyon_model
declare -r VERSION_NAME=v1

echo
echo "Using model version: " $MODEL_VERSION
set -v -e

# Takes about 30 mins to preprocess everything.  We serialize the two
# preprocess.py synchronous calls just for shell scripting ease; you could use
# --runner DataflowRunner to run them asynchronously.  Typically,
# the total worker time is higher when running on Cloud instead of your local
# machine due to increased network traffic and the use of more cost efficient
# CPU's.  Check progress here: https://console.cloud.google.com/dataflow

gsutil -m rsync -r "${GCS_PATH}/equipmentparts_1_1516157584" "gs://${PROJECT}-training/${MODEL_NAME}/equipmentparts_1_1516157584"




# Training on CloudML is quick after preprocessing.  If you ran the above
# commands asynchronously, make sure they have completed before calling this one.
gcloud ml-engine jobs submit training "equipmentparts_1_1516157584" \
  --stream-logs \
  --module-name trainer.task \
  --package-path trainer \
  --staging-bucket "gs://${PROJECT}-training/" \
  --region $REGION \
  --runtime-version=1.2 \
  --config cloudml-config.yaml \
  -- \
  --output_path "gs://${PROJECT}-model-output/${MODEL_NAME}/equipmentparts_1_1516157584" \
  --eval_data_paths "gs://${PROJECT}-training/${MODEL_NAME}/equipmentparts_1_1516157584/preproc/eval*" \
  --train_data_paths "gs://${PROJECT}-training/${MODEL_NAME}/equipmentparts_1_1516157584/preproc/train*" \
  --label_count=3
