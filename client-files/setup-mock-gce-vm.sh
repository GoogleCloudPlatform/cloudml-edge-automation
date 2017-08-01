#!/bin/bash

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


# This script prepares a GCE Ubuntu instance as a mock edge device which will
# run the Kubernetes kubelet and docker as a way of automating the delivery
# of machine learning trained models


group=docker
sudo groupadd docker
sudo usermod -aG docker $USER

if [ $(id -gn) != $group ]; then
  echo "switching groups"
  exec sg $group "$0"
fi

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo add-apt-repository    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"
sudo apt-get update && sudo apt-get install -y docker-ce

wget https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-165.0.0-linux-x86_64.tar.gz
tar -xvzf google-cloud-sdk*

./google-cloud-sdk/install.sh --quiet --additional-components=docker-credential-gcr --path-update=True
. ~/google-cloud-sdk/path.bash.inc
docker-credential-gcr configure-docker

gsutil cp gs://kubernetes-release/release/v1.7.0/bin/linux/amd64/kubelet .
chmod +x kubelet 
sudo mv kubelet /usr/local/bin/

# create the local folder where pod yaml will be stored
sudo mkdir -p /opt/device/pods/

# create the local folder that mounts into the ML model server and allows images to be read
sudo mkdir -p /tmp/images
sudo chmod 777 /tmp/images

# we are going to run the kubelet with systemd
sudo mv /tmp/kubelet.service /etc/systemd/system/kubelet.service

sudo chown root:root /etc/systemd/system/kubelet.service
sudo chmod 644 /etc/systemd/system/kubelet.service
sudo systemctl daemon-reload
sudo systemctl start kubelet.service
