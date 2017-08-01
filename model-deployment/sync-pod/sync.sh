#!/usr/bin/sh

# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

mkdir -p /device/pod_src1/ /device/pod_src2/ /device/stage_pods/ /device/pods/

while :;
do
gsutil -m rsync -d gs://${PROJECT}-deploy/${ARCH}/all/ /device/pod_src1/

gsutil -m rsync -d gs://${PROJECT}-deploy/${ARCH}/${TRACK}/ /device/pod_src2/

rm /device/stage_pods/*

cp /device/pod_src1/* /device/stage_pods/

cp /device/pod_src2/* /device/stage_pods/

rsync -av --delete /device/stage_pods/ /device/pods/

/bin/sleep 20

done
