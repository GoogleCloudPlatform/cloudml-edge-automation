/**
 * Copyright 2017, Google, Inc.
 * Licensed under the Apache License, Version 2.0 (the `License`);
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an `AS IS` BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

'use strict';

var request = require('request');
var GoogleAuth = require('google-auth-library');
var Storage = require('@google-cloud/storage');
var Mustache = require('mustache');

var authFactory = new GoogleAuth();

function getTagParts (fullTag) {
  var name, tag, host, project, image;
  [name, tag] = fullTag.split(':');
  [host, project, image] = name.split('/');
  return [host, project, image, tag];
}

function getDigestFromTag (fullTag, callback) {
  var tag, host, project, image, digest;
  [host, project, image, tag] = getTagParts(fullTag);
  authFactory.getApplicationDefault(function (err, authClient) {
    if (err) {
      console.log('Authentication failed because of ', err);
      return;
    }
    authClient.getAccessToken(function (err, token, response) {
      if (err) {
        console.log('Error: ' + err);
      }
      request(
        {
          'method': 'HEAD',
          'uri': 'https://' + host + '/v2/' + project + '/' + image + '/manifests/' + tag,
          'headers': {
            'Authorization': 'Bearer ' + token,
            'Accept': 'application/vnd.docker.distribution.manifest.v2+json'
          }
        }, function (err, response, body) {
        if (err) {
          console.log('Error: ' + err);
        }
        digest = response.headers['docker-content-digest'];
        callback(digest);
      });
    });
  });
}

exports.tagMonitor = function (event, callback) {
  const pubsubMessage = event.data;
  const eventDataRaw = pubsubMessage.data ? Buffer.from(pubsubMessage.data, 'base64').toString() : '{"action": "none"}';
  const eventData = JSON.parse(eventDataRaw);
  console.log(eventData);
  var host, project, image, tag;

  if (eventData.action !== 'INSERT') {
    // we only want insertion events
    console.log('non insert event');
    callback();
    return;
  }

  if (eventData.tag === undefined) {
    // we only want tag, not digest events
    console.log('non tag event');
    callback();
    return;
  }

  const fullTag = eventData.tag;
  [host, project, image, tag] = getTagParts(fullTag);

  const validTags = ['latest', 'alpha', 'beta', 'stable'];
  if (validTags.indexOf(tag) < 0) {
    // there are only certain release tags we are interested in
    console.log('non release tag' + tag);
    callback();
    return;
  }

  // at this point, we should have a tag of interest
  console.log(eventData.tag);

  const gcs = Storage({
    projectId: project
  });

  getDigestFromTag(fullTag, function (digest) {
    console.log(digest);
    var values = {
      'host': host,
      'project': project,
      'image': image,
      'digest': digest
    };
    var arch = image.split('-').pop();
    const bucket = gcs.bucket(project + '-deploy');
    var file = bucket.file('templates/' + image + '-pod.yaml.templ');
    file.download().then(function (data) {
      const contents = data[0].toString();
      var output = Mustache.render(contents, values);
      var yamlTarget = arch + '/' + tag + '/' + image + '-pod.yaml';
      var file = bucket.file(yamlTarget);
      var fd = file.createWriteStream();
      fd.write(output);
      fd.end();
      console.log('updated ' + yamlTarget);
      callback();
    }).catch(function (e) {
      console.log(e);
      callback();
    });
  });
};
