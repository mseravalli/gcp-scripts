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

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

def GlobalComputeUrl(project, collection, name):
  """Generate global compute URL."""
  return ''.join([COMPUTE_URL_BASE, 'projects/', project, '/global/', collection, '/', name])

def RegionalComputeUrl(project, region, collection, name):
  """Generate regional compute URL."""
  return ''.join([COMPUTE_URL_BASE, 'projects/', project, '/regions/', region, '/', collection, '/', name])

def GenerateConfig(context):
  """Generates config."""

  project_id = context.env['project']
  project_number = str(context.env['project_number'])
  environment = str(context.properties.get('environment', ''))
  if environment != '':
    environment = '-' + environment

  sa_compute_default_full = project_number + '-compute' + '@developer.gserviceaccount.com'
  sa_dm_default_full = project_number + '@cloudservices.gserviceaccount.com'

  sa_hana_compute = 'sa-hana-vm' + environment
  sa_hana_compute_full = sa_hana_compute + '@' + project_id + '.iam.gserviceaccount.com'

  instance_name = str(context.properties.get('instanceName')) + environment

  # defines all the resources that will be deployed
  resources = []

  # create service account for VM and allow DM to use it
  resources.append({
    'name': sa_hana_compute,
    'type': 'iam.v1.serviceAccount',
    'properties': {
      'accountId': sa_hana_compute,
      'displayName': sa_hana_compute,
      'projectId': project_id
    },
    'accessControl': {
      'gcpIamPolicy': {
        'bindings': [ {
          'role': 'roles/iam.serviceAccountUser',
          'members': [
            'serviceAccount:' + sa_dm_default_full,
            'serviceAccount:' + sa_hana_compute_full,
          ]
        } ]
      }
    }
  })

  # update permissions for service accounts
  # TODO: first delete all the existing policies for the service accounts
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
    # Set the IAM policy patching the existing policy with what ever is currently in the config.
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
              'serviceAccount:' + sa_hana_compute_full
            ]
          }, {
            # this might be needed in the host project of the XPN
            'role': 'roles/compute.networkUser',
            'members': [
              'serviceAccount:' + sa_hana_compute_full
            ]
          }, {
            'role': 'roles/compute.instanceAdmin.v1',
            'members': [
              'serviceAccount:' + sa_hana_compute_full,
            ]
          }, {
            'role': 'roles/logging.logWriter',
            'members': [
              'serviceAccount:' + sa_hana_compute_full,
            ]
          }, {
            'role': 'roles/monitoring.metricWriter',
            'members': [
              'serviceAccount:' + sa_hana_compute_full,
            ]
          }
        ]
      }
    },
    'metadata': {
      'dependsOn': [sa_hana_compute, project_id + '-get-iam-policy']
    }
  }])

  # update firewalls
  resources.append({
    'name': 'hana-fw-rule',
    'type': 'compute.v1.firewall',
    'properties': {
      #'network': '$(ref.{{' + context.env['deployment'] +'}}-network.selfLink)',
      'network': GlobalComputeUrl(project_id, 'networks', 'default'),
      'direction': 'INGRESS',
      'sourceRanges': [
        '0.0.0.0/0'
      ],
      'allowed': [{
        'IPProtocol': 'all'
      }],
      'targetServiceAccounts': [
        '149382556458-compute@developer.gserviceaccount.com'
      ]
    }
  })

  # install sap_hana
  resources.append({
    'name': 'sap_hana',
    'type': 'sap_hana.py',
    'properties': {
      'instanceName': instance_name,
      'instanceType': str(context.properties.get('instanceType')),
      'zone': str(context.properties.get('zone')),
      'subnetwork': str(context.properties.get('subnetwork')),
      'linuxImage': str(context.properties.get('linuxImage')),
      'linuxImageProject': str(context.properties.get('linuxImageProject')),
      'deployment_script_location': str(context.properties.get('deployment_script_location')),
      'sap_hana_deployment_bucket': str(context.properties.get('sap_hana_deployment_bucket')),
      'sap_hana_sid': str(context.properties.get('sap_hana_sid')),
      'sap_hana_instance_number': int(context.properties.get('sap_hana_instance_number')),
      'sap_hana_sidadm_password': str(context.properties.get('sap_hana_sidadm_password')),
      'sap_hana_system_password': str(context.properties.get('sap_hana_system_password')),
      'sap_hana_scaleout_nodes': int(context.properties.get('sap_hana_scaleout_nodes')),
      'sap_deployment_debug': bool(context.properties.get('sap_deployment_debug')),
      'sap_hana_sidadm_uid': int(context.properties.get('sap_hana_sidadm_uid')),
      'serviceAccount': sa_hana_compute_full
    },
    'metadata': {
      'dependsOn': [project_id + '-patch-iam-policy']
    }
  })

  return {'resources': resources}


