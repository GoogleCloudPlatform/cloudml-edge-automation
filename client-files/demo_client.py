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
import sys
import urllib2

url = 'http://localhost:5000/predict/'  # Set destination URL here


if len(sys.argv) > 1:
    path = sys.argv[1]
else:
    path = "/tmp/test_image.jpg"

post_fields = {'path': path}     # Set POST fields here

req_data = json.dumps(post_fields)
request = urllib2.Request(url, data=req_data)
json = urllib2.urlopen(request).read().decode()
print(json)
