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

  project_id = context.env['project']
  project_number = str(context.env['project_number'])
  environment = str(context.properties.get('environment'))

  resources = []

  # create service account for VM
  sa_name = 'sa-' + project_number + '-' + environment + '-hana-vm'
  resources.append({
    'name': sa_name,
    'type': 'iam.v1.serviceAccount',
    'properties': {
      'accountId': sa_name,
      'displayName': sa_name,
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
            'role': 'roles/owner',
            'members': [
              # default agent for Compute
              'serviceAccount:' + project_number + '-compute@developer.gserviceaccount.com',
              # custom service account hana vm
              'serviceAccount:' + sa_name + '@' + project_id + '.iam.gserviceaccount.com'
            ]
          },
          {
            'role': 'roles/compute.serviceAgent',
            'members': [
              # default agent for DM
              'serviceAccount:' + project_number + '@cloudservices.gserviceaccount.com'
            ]
          }
        ]
      }
    },
    'metadata': {
      'dependsOn': [sa_name, project_id + '-get-iam-policy']
    }
  }])

  return {'resources': resources}


