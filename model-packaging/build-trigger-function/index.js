/* jslint es6 */

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

var google = require('googleapis');

const DEPLOY_ONLINE = true;

/**
 * Background Cloud Function to be triggered by Cloud Storage.
 *
 * @param {object} event The Cloud Functions event.
 * @param {function} callback The callback function.
 */
exports.modelDoneWatcher = function (event, callback) {
  console.log(event);
  const file = event.data;
  if (file.resourceState === 'not_exists') {
    console.log(`File ${file.name} deleted.`);
  } else if (file.metageneration === '1') {
    // metageneration attribute is updated on metadata changes.
    // on create value is 1

    var project = file.bucket.substring(0, file.bucket.indexOf('-model-output'));
    // console.log(`File ${file.name} uploaded.`);
    var parts = file.name.split('/');
    // the 'trainer-done' file is placed in the output directory as the final
    // step of the machine learning training job.
    if (parts[parts.length - 1] === 'TRAINER-DONE') {
      var mljobid = parts[1];
      var modelName = parts[0];
      // var idElements = mljobid.split('_');
      console.log('Job done: ', mljobid);
      var archs = ['-armv7l', '-x86_64'];
      var arch = '';
      var job = {};
      var arrayLength = archs.length;
      google.auth.getApplicationDefault(function (err, authClient, projectId) {
        if (err) {
          throw err;
        }

        if (authClient.createScopedRequired && authClient.createScopedRequired()) {
          // Scopes can be specified either as an array or as a single, space-delimited string.
          authClient = authClient.createScoped([
            'https://www.googleapis.com/auth/cloud-platform'
          ]);
        }

        var cloudbuild = google.cloudbuild({
          version: 'v1',
          auth: authClient
        });

        for (var i = 0; i <= arrayLength; i++) {
          arch = archs[i];
          console.log('Submitting build for ' + arch);
          job = undefined;
          job = {
            'images': [
              'gcr.io/' + project + '/' + modelName.toLowerCase() + arch
            ],
            'projectId': project,

            'source': {
              'repoSource': {
                'projectId': project,
                'repoName': 'ml-automation',
                'branchName': 'master'
              }
            },

            'steps': [
              {
                'args': [
                  'rsync',
                  '-r',
                  'gs://' + file.bucket + '/' + parts.slice(0, parts.length - 1).join('/') + '/',
                  './'
                ],
                'id': 'copy_a',
                'name': 'gcr.io/cloud-builders/gsutil'
              },
              {
                'args': [
                  'build',
                  '-t',
                  'gcr.io/' + project + '/' + modelName.toLowerCase() + arch + ':' + mljobid.toLowerCase(),
                  '-t',
                  'gcr.io/' + project + '/' + modelName.toLowerCase() + arch + ':latest',
                  '-f',
                  'model-packaging/dockerfile-model-serve' + arch,
                  '.'
                ],
                'name': 'gcr.io/cloud-builders/docker',
                'waitFor': [
                  'copy_a'
                ]
              }
            ],
            'timeout': '600s'
          };
          console.log(job);

          cloudbuild.projects.builds.create({projectId: project, resource: job}, function (err, result) {
            console.log(err, result);
          });
          job = undefined;
        } // end for loop

        if (DEPLOY_ONLINE) {
          // also deploy online prediction
          var ml = google.ml({version: 'v1', auth: authClient});
          var model = {
            'name': modelName,
            'description': 'Automated ML model',
            'onlinePredictionLogging': true
          };

          var modelVersion = {
            'name': mljobid,
            'description': 'Automated ML model',
            'deploymentUri': 'gs://' + file.bucket + '/' + parts.slice(0, parts.length - 1).join('/') + '/'
          };

          var parent = 'projects/' + project;
          var modelParent = 'projects/' + project + '/models/' + modelName;

          ml.projects.models.create({parent: parent, resource: model},
            function (err, result) {
              console.log(err, result);
              ml.projects.models.versions.create({parent: modelParent, resource: modelVersion},
                function (err, result) {
                  console.log(err, result);
                });
            });
        }
      });
    }
  }
  callback();
};
