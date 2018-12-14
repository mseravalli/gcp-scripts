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

import re

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

def GlobalComputeUrl(project, collection, name):
  """Generate global compute URL."""
  return ''.join([COMPUTE_URL_BASE, 'projects/', project, '/global/', collection, '/', name])

def RegionalComputeUrl(project, region, collection, name):
  """Generate regional compute URL."""
  return ''.join([COMPUTE_URL_BASE, 'projects/', project, '/regions/', region, '/', collection, '/', name])

def AddServiceAccount(resources, project_id, sa_hana_compute_full, sa_dm_default_full):
  # create service account for VM and allow DM to use it
  resources.append({
    'name': sa_hana_compute_full,
    'type': 'iam.v1.serviceAccount',
    'properties': {
      'accountId': re.sub(r'@.*', '', sa_hana_compute_full),
      'displayName': 'Service Account for SAP Hana',
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

# Update bindings and roles associated to service accounts.
# If the template is run more that a single time, ensure to remove all the
# roles associated to the `hana_compute` service account.
# If not all existing roles are deleted, the policies will not be correctly applied.
# This is due to the fact that the policies are associated to the internal id
# of a service account (!= from the email), but only the email is displayed. 
# In the case that serviceaccount@myproject.com is deleted and recreated,
# as long as there is a policy associated to the service account email, in the
# background the old id will be used, the new service account will not inherit
# the policies of its predecessor. All policies need to be deleted first, only
# after this operations the newer service account will be used.
def UpdateServiceAccountPermissions(resources, project_id, sa_hana_compute_full, context):

  # no dependency if no serviceAccount is defined
  # TODO: case where the service account is in a different project
  sa_dependency = []
  if (str(context.properties.get('serviceAccount', ''))  != '') :
    sa_dependency = [sa_hana_compute_full]

  resources.extend([{
    # Get the IAM policy first so that we do not remove any existing bindings.
    'name': 'get-iam-policy-initial',
    'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.getIamPolicy',
    'properties': {
      'resource': project_id,
    },
    'metadata': {
      'dependsOn': sa_dependency,
      'runtimePolicy': ['UPDATE_ALWAYS']
    }
  }, {
    # Set the IAM policy patching the existing policy with what ever is currently in the config.
    'name': 'patch-remove-iam-policy',
    'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.setIamPolicy',
    'properties': {
      'resource': project_id,
      'policy': '$(ref.get-iam-policy-initial)',
      'gcpIamPolicyPatch': {
        'remove': [
          {
            'role': 'roles/storage.objectAdmin',
            'members': [
              'serviceAccount:' + sa_hana_compute_full
            ]
          }, {
            # TODO: permission needs to be in the right project in case of XPN
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
      'dependsOn': ['get-iam-policy-initial'],
      'runtimePolicy': ['UPDATE_ALWAYS']
    }
  }, {
    # Get the IAM policy first so that we do not remove any existing bindings.
    'name': 'get-iam-policy-cleaned',
    'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.getIamPolicy',
    'properties': {
      'resource': project_id,
    },
    'metadata': {
      'dependsOn': ['patch-remove-iam-policy'],
      'runtimePolicy': ['UPDATE_ALWAYS']
    }
  }, {
    # Set the IAM policy patching the existing policy with what ever is currently in the config.
    'name': 'patch-add-iam-policy',
    'action': 'gcp-types/cloudresourcemanager-v1:cloudresourcemanager.projects.setIamPolicy',
    'properties': {
      'resource': project_id,
      'policy': '$(ref.get-iam-policy-cleaned)',
      'gcpIamPolicyPatch': {
        'add': [
          {
            'role': 'roles/storage.objectAdmin',
            'members': [
              'serviceAccount:' + sa_hana_compute_full
            ]
          }, {
            # TODO: permission needs to be in the right project in case of XPN
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
      'dependsOn': ['get-iam-policy-cleaned'],
      'runtimePolicy': ['UPDATE_ALWAYS']
    }
  }])

"""Allow full communication between SAP HANA VM"""
def AddFirewallRules(resources, project_id, sa_hana_compute_full, context):
  # no dependency if no serviceAccount is defined
  # TODO: case where the service account is in a different project
  sa_dependency = []
  if (str(context.properties.get('serviceAccount', ''))  != '') :
    sa_dependency = [sa_hana_compute_full]

  resources.extend([{
    'name': 'allow-hana-internal',
    'type': 'compute.v1.firewall',
    'properties': {
      #'network': '$(ref.{{' + context.env['deployment'] +'}}-network.selfLink)',
      'network': GlobalComputeUrl(project_id, 'networks', 'default'),
      'direction': 'INGRESS',
      'sourceServiceAccounts': [
        sa_hana_compute_full
      ],
      'allowed': [{
        'IPProtocol': 'all'
      }],
      'targetServiceAccounts': [
        sa_hana_compute_full
      ]
    },
    'metadata': {
      'dependsOn': sa_dependency
    }
  }])

def InstallSAPHana(resources, context):
  resources.append({
    'name': 'sap_hana',
    'type': 'sap_hana.py',
    'properties': {
      'instanceName': str(context.properties.get('instanceName')),
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
      'serviceAccount': str(context.properties.get('serviceAccount'))
    },
    'metadata': {
      'dependsOn': ['patch-add-iam-policy']
    }
  })

def GenerateConfig(context):
  """Generates config."""

  # defines all the resources that will be deployed
  resources = []

  project_id = context.env['project']
  project_number = str(context.env['project_number'])

  sa_compute_default_full = project_number + '-compute' + '@developer.gserviceaccount.com'
  sa_dm_default_full = project_number + '@cloudservices.gserviceaccount.com'

  # by default use the default compute service account
  sa_hana_compute_full = sa_compute_default_full

  if (str(context.properties.get('serviceAccount', ''))  != '') :
    # if complete email is not provided define the service account for current project
    if "@" in context.properties['subnetwork']:
      sa_hana_compute_full = str(context.properties.get('serviceAccount')) 
    else:
      sa_hana_compute_full = str(context.properties.get('serviceAccount')) + '@' + project_id + '.iam.gserviceaccount.com'

    context.properties['serviceAccount'] = sa_hana_compute_full
    AddServiceAccount(resources, project_id, sa_hana_compute_full, sa_dm_default_full)

  UpdateServiceAccountPermissions(resources, project_id, sa_hana_compute_full, context)

  AddFirewallRules(resources, project_id, sa_hana_compute_full, context)

  context.properties['serviceAccount'] = sa_hana_compute_full
  InstallSAPHana(resources, context)

  return {'resources': resources}


