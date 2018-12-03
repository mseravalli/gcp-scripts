# Copyright 2018 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Creates the infrastructure and deploys HANA"""

def GenerateConfig(context):
  """Generates config."""

  project_id = context.properties['project_id']

  resources = []

  # create bucket for installation files
  bucket_name = project_id + '-hanainstallation09876493'
  resources.append({
    'name': bucket_name,
    'type': 'storage.v1.bucket'
  })

  # create service account for VM
  sa_name = project_id + '-sa-hana-vm'
  resources.append({
    'name': sa_name,
    'type': 'iam.v1.serviceAccount',
    'properties': {
      'accountId': project_id + '-sa-hana-vm',
      'displayName': project_id + '-sa-hana-vm',
      'projectId': project_id
    }
  })

  # update permissions for service account
  resources.extend([{
    # Get the IAM policy first so that we do not remove any existing bindings.
    'name': project_id + '-get-iam-policy',
    'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.getIamPolicy',
    'properties': {
      'resource': project_id,
    },
    'metadata': {
      'runtimePolicy': ['UPDATE_ALWAYS']
    }
  }, {
    # Set the IAM policy patching the existing policy with what ever is currently in the
    # config.
    'name': project_id + '-patch-iam-policy',
    'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.setIamPolicy',
    'properties': {
      'resource': project_id,
      'policy': '$(ref.' + project_id + '-get-iam-policy)',
      'gcpIamPolicyPatch': {
        'add': [
          {
            'role': 'roles/storage.objectAdmin',
            'members': [
              'serviceAccount:'+sa_name+'@'+project_id+'.iam.gserviceaccount.com'
            ]
          }
        ]
      }
    },
    'metadata': {
      'dependsOn': [bucket_name, sa_name, project_id + '-get-iam-policy']
    }
  }])


  return {'resources': resources}


