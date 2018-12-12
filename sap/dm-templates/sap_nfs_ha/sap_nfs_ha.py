# ------------------------------------------------------------------------
# Copyright 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Description:  Google Cloud Platform - SAP Deployment Functions
# Build Date:   Fri Nov 30 14:59:44 GMT 2018
# ------------------------------------------------------------------------

"""Creates a Compute Instance with the provided metadata."""

COMPUTE_URL_BASE = 'https://www.googleapis.com/compute/v1/'

def GlobalComputeUrl(project, collection, name):
  return ''.join([COMPUTE_URL_BASE, 'projects/', project,
                  '/global/', collection, '/', name])

def ZonalComputeUrl(project, zone, collection, name):
  return ''.join([COMPUTE_URL_BASE, 'projects/', project,
                  '/zones/', zone, '/', collection, '/', name])

def RegionalComputeUrl(project, region, collection, name):
  return ''.join([COMPUTE_URL_BASE, 'projects/', project,
                  '/regions/', region, '/', collection, '/', name])

def GenerateConfig(context):
  """Generate configuration."""

  # Get/generate variables from context
  primary_instance_name = context.properties['primaryInstanceName']
  secondary_instance_name = context.properties['secondaryInstanceName']
  primary_zone = context.properties['primaryZone']
  secondary_zone = context.properties['secondaryZone']
  project = context.env['project']
  primary_instance_type = ZonalComputeUrl(project, primary_zone, 'machineTypes', context.properties['instanceType'])
  secondary_instance_type = ZonalComputeUrl(project, secondary_zone, 'machineTypes', context.properties['instanceType'])
  region = context.properties['primaryZone'][:context.properties['primaryZone'].rfind('-')]
  linux_image_project = context.properties['linuxImageProject']
  linux_image = GlobalComputeUrl(linux_image_project, 'images', context.properties['linuxImage'])
  deployment_script_location = str(context.properties.get('deployment_script_location', 'https://storage.googleapis.com/sapdeploy/dm-templates'))
  primary_startup_url = "curl " + deployment_script_location + "/sap_nfs_ha/startup.sh | bash -s " + deployment_script_location
  secondary_startup_url = "curl " + deployment_script_location + "/sap_nfs_ha/startup_secondary.sh | bash -s " + deployment_script_location
  service_account = str(context.properties.get('serviceAccount', context.env['project_number'] + '-compute@developer.gserviceaccount.com'))
  network_tags = { "items": str(context.properties.get('networkTag', '')).split(',') if len(str(context.properties.get('networkTag', ''))) else [] }

  ## Get deployment template specific variables from context
  sap_vip = str(context.properties.get('sap_vip', ''))
  sap_vip_secondary_range = str(context.properties.get('sap_vip_secondary_range', ''))
  nfs_vol_size = int(context.properties.get('nfsVolSize', '10'))
  sap_deployment_debug = str(context.properties.get('sap_deployment_debug', 'False')) 
  post_deployment_script = str(context.properties.get('post_deployment_script', ''))

  # Subnetwork: with SharedVPC support
  if "/" in context.properties['subnetwork']:
      sharedvpc = context.properties['subnetwork'].split("/")
      subnetwork = RegionalComputeUrl(sharedvpc[0], region, 'subnetworks', sharedvpc[1])
  else:
      subnetwork = RegionalComputeUrl(project, region, 'subnetworks', context.properties['subnetwork'])

  # Public IP
  if str(context.properties['publicIP']) == "False":
      networking = [ ]
  else:
      networking = [{
        'name': 'external-nat',
        'type': 'ONE_TO_ONE_NAT'
      }]

  # set startup URL
  if sap_deployment_debug == "True":
      primary_startup_url = primary_startup_url.replace(" -s ", " -x -s ")
      secondary_startup_url = secondary_startup_url.replace(" -s "," -x -s ")      

  ## compile complete json
  instance_name=context.properties['primaryInstanceName']

  nfs_nodes = []

  nfs_nodes.append({
          'name': instance_name + '-nfsvol',
          'type': 'compute.v1.disk',
          'properties': {
              'zone': primary_zone,
              'sizeGb': nfs_vol_size,
              'type': ZonalComputeUrl(project, primary_zone, 'diskTypes','pd-standard')
              }
          })

  nfs_nodes.append({
          'name': instance_name,
          'type': 'compute.v1.instance',
          'properties': {
              'zone': primary_zone,
              'machineType': primary_instance_type,
              'metadata': {
                  'items': [{
                      'key': 'startup-script',
                      'value': primary_startup_url
                  },
                  {
                      'key': 'sap_primary_instance',
                      'value': primary_instance_name
                  },
                  {
                      'key': 'sap_secondary_instance',
                      'value': secondary_instance_name
                  },
                  {
                      'key': 'sap_primary_zone',
                      'value': primary_zone
                  },
                  {
                      'key': 'sap_secondary_zone',
                      'value': secondary_zone
                  },                  
                  {
                      'key': 'sap_deployment_debug',
                      'value': sap_deployment_debug
                  },
                  {
                      'key': 'post_deployment_script',
                      'value': post_deployment_script
                  },                  
                  {
                      'key': 'sap_vip',
                      'value': sap_vip
                  },
                  {
                      'key': 'sap_vip_secondary_range',
                      'value': sap_vip_secondary_range
                  }]
              },
              "tags": network_tags,
              'disks': [{
                  'deviceName': 'boot',
                  'type': 'PERSISTENT',
                  'autoDelete': True,
                  'boot': True,
                  'initializeParams': {
                      'diskName': instance_name + '-boot',
                      'sourceImage': linux_image,
                      'diskSizeGb': '30'
                      }
                  },
                  {
                  'deviceName': instance_name + '-nfsvol',
                  'type': 'PERSISTENT',
                  'source': ''.join(['$(ref.', instance_name + '-nfsvol', '.selfLink)']),
                  'autoDelete': True
                  }],
              'canIpForward': True,
              'serviceAccounts': [{
                  'email': service_account,
                  'scopes': [
                      'https://www.googleapis.com/auth/compute',
                      'https://www.googleapis.com/auth/servicecontrol',
                      'https://www.googleapis.com/auth/service.management.readonly',
                      'https://www.googleapis.com/auth/logging.write',
                      'https://www.googleapis.com/auth/monitoring.write',
                      'https://www.googleapis.com/auth/trace.append',
                      'https://www.googleapis.com/auth/devstorage.read_write'
                      ]
                  }],
              'networkInterfaces': [{
                  'accessConfigs': networking,
                    'subnetwork': subnetwork
                  }]
              }

          })

  ## create secondary node
  instance_name=context.properties['secondaryInstanceName']

  nfs_nodes.append({
          'name': instance_name + '-nfsvol',
          'type': 'compute.v1.disk',
          'properties': {
              'zone': secondary_zone,
              'sizeGb': nfs_vol_size,
              'type': ZonalComputeUrl(project, secondary_zone, 'diskTypes','pd-standard')
              }
          })

  nfs_nodes.append({
          'name': instance_name,
          'type': 'compute.v1.instance',
          'properties': {
              'zone': secondary_zone,
              'machineType': secondary_instance_type,
              'metadata': {
                  'items': [{
                      'key': 'startup-script',
                      'value': secondary_startup_url
                  },
                  {
                      'key': 'sap_primary_instance',
                      'value': primary_instance_name
                  },
                  {
                      'key': 'sap_secondary_instance',
                      'value': secondary_instance_name
                  },
                  {
                      'key': 'sap_primary_zone',
                      'value': primary_zone
                  },
                  {
                      'key': 'sap_secondary_zone',
                      'value': secondary_zone
                  },                  
                  {
                      'key': 'sap_deployment_debug',
                      'value': sap_deployment_debug
                  },
                  {
                      'key': 'post_deployment_script',
                      'value': post_deployment_script
                  },                  
                  {
                      'key': 'sap_vip',
                      'value': sap_vip
                  },
                  {
                      'key': 'sap_vip_secondary_range',
                      'value': sap_vip_secondary_range
                  }]
              },
              "tags": network_tags,
              'disks': [{
                  'deviceName': 'boot',
                  'type': 'PERSISTENT',
                  'autoDelete': True,
                  'boot': True,
                  'initializeParams': {
                      'diskName': instance_name + '-boot',
                      'sourceImage': linux_image,
                      'diskSizeGb': '30'
                      }
                  },
                  {
                  'deviceName': instance_name + '-nfsvol',
                  'type': 'PERSISTENT',
                  'source': ''.join(['$(ref.', instance_name + '-nfsvol', '.selfLink)']),
                  'autoDelete': True
                  }],
              'canIpForward': True,
              'serviceAccounts': [{
                  'email': service_account,
                  'scopes': [
                      'https://www.googleapis.com/auth/compute',
                      'https://www.googleapis.com/auth/servicecontrol',
                      'https://www.googleapis.com/auth/service.management.readonly',
                      'https://www.googleapis.com/auth/logging.write',
                      'https://www.googleapis.com/auth/monitoring.write',
                      'https://www.googleapis.com/auth/trace.append',
                      'https://www.googleapis.com/auth/devstorage.read_write'
                      ]
                  }],
              'networkInterfaces': [{
                  'accessConfigs': networking,
                    'subnetwork': subnetwork
                  }]
          }
    })

  return {'resources': nfs_nodes}
