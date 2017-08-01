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

import json
import os

from flask import Flask
from flask import jsonify
from flask import request

from infer import Session

app = Flask(__name__)

#  TODO note, this is not thread safe and will only work with Flask in single
#  thread single process mode
#  global app_session
tf_session = Session()

app.version = os.getenv("CONTAINER_DIGEST", "unknown")


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/version/")
def get_version():
    return jsonify({"version": app.version})


@app.route("/predict/", methods=["POST"])
def predict():
    #  Sending without header
    raw = request.get_data()
    req = json.loads(raw)
    print(req)
    result = tf_session.infer(req["path"])
    #  return "OK"
    return jsonify(result)
