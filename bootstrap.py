#!/usr/bin/env python

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

"""
This script is used to bootstrap some yaml files in this repository to be
configured to a different target project. By default the files assume the
original project is cad-iot-ml, and the target project should be in the
environment variable PROJECT
"""
import os
import sys
from shutil import copyfile

project = os.getenv("PROJECT")
from_project = os.getenv("FROM_PROJECT", "cad-iot-ml")


def update_project(sub):
    for dname, dirs, files in os.walk(sub):
        for fname in files:
            fpath = os.path.join(dname, fname)
            with open(fpath) as f:
                s = f.read()
            s = s.replace(from_project, project)
            with open(fpath, "w") as f:
                f.write(s)


if __name__ == "__main__":
    if project is None:
        sys.exit("You need to set the PROJECT environment variable and \
                run again")

    sync_template = "model-deployment/sync-pod.yaml.templ"

    templ = open(sync_template).read()
    dir_path = os.path.dirname(os.path.realpath(__file__))

    #  for each "release" track and CPU architecture, generate a "sync" pod
    #  that will handle GCS syncronization for a given target device group
    for arch in ["x86_64", "armv7l"]:
        for track in ["latest", "alpha", "beta", "stable"]:
            rendered = templ.replace("{{PROJECT}}", project)
            rendered = rendered.replace("{{ARCH}}", arch)
            rendered = rendered.replace("{{TRACK}}", track)
            path = os.path.join(dir_path, "model-deployment",
                                "deploy-bucket-bootstrap", arch, track)
            fpath = os.path.join(path, "sync-pod.yaml")
            try:
                os.makedirs(path)
            except:
                pass
            with open(fpath, 'w') as f:
                f.write(rendered)

    os.makedirs("model-deployment/deploy-bucket-bootstrap/templates")
    copyfile(os.path.join(dir_path, "model-deployment",
            "equipmentparts-x86_64-pod.yaml.templ"),
            "model-deployment/deploy-bucket-bootstrap/templates/equipmentparts-x86_64-pod.yaml.templ")
    copyfile(os.path.join(dir_path, "model-deployment",
            "equipmentparts-armv7l-pod.yaml.templ"),
            "model-deployment/deploy-bucket-bootstrap/templates/equipmentparts-armv7l-pod.yaml.templ")
    copyfile(os.path.join(dir_path, "model-deployment",
            "simple-web-test", "hello-armv7l-pod.yaml.templ"),
            "model-deployment/deploy-bucket-bootstrap/templates/hello-armv7l-pod.yaml.templ")
    copyfile(os.path.join(dir_path, "model-deployment",
            "simple-web-test", "hello-x86_64-pod.yaml.templ"),
            "model-deployment/deploy-bucket-bootstrap/templates/hello-x86_64-pod.yaml.templ")

    update_project("model-deployment/simple-web-test/")
    update_project("model-packaging")
