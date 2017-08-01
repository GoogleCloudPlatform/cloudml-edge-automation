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

import os
import sys

import numpy as np
import tensorflow as tf
from tensorflow.contrib.saved_model.python.saved_model import signature_def_utils
from tensorflow.python.saved_model import signature_constants
from tensorflow.python.saved_model import tag_constants


class Session(object):
    def __init__(self):

        model_path = os.environ.get('MODEL_PATH', '/model')

        self.sess = tf.Session(graph=tf.Graph())
        saved_metagraphdef = tf.saved_model.loader.load(self.sess,
                [tag_constants.SERVING], model_path)

        self.inputs_tensor_info = signature_def_utils.get_signature_def_by_key(
                saved_metagraphdef,
                signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY).inputs
        outputs_tensor_info = signature_def_utils.get_signature_def_by_key(
                saved_metagraphdef,
                signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY).outputs

        self.output_tensor_keys_sorted = sorted(outputs_tensor_info.keys())
        self.output_tensor_names_sorted = [
           outputs_tensor_info[tensor_key].name
           for tensor_key in self.output_tensor_keys_sorted
           ]

    def infer(self, path):
        img = open(path, "rb").read()
        inputs_dict = {"key": "0", "image_bytes": str(img)}
        inputs_dict = {k: np.array([v]) for k, v in inputs_dict.iteritems()}

        inputs_feed_dict = {
           self.inputs_tensor_info[key].name: tensor
           for key, tensor in inputs_dict.items()
           }

        tf_out = self.sess.run(self.output_tensor_names_sorted,
                feed_dict=inputs_feed_dict)
        result = []
        for i, output in enumerate(tf_out):
            output_tensor_key = self.output_tensor_keys_sorted[i]
            if output_tensor_key == "scores":
                for j, val in enumerate(output[0]):
                    result.append(("part-%s" % (j + 1), float(val)))
            results = sorted(result, key=lambda x: x[1], reverse=True)
        return results


def main():
    s = Session()
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "/tmp/test_image.jpg"

    print(s.infer(path))


if __name__ == "__main__":
    main()
