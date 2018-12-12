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
  """Generate global compute URL."""
  return ''.join([COMPUTE_URL_BASE, 'projects/', project, '/global/', collection, '/', name])


def ZonalComputeUrl(project, zone, collection, name):
  """Generate zone compute URL."""
  return ''.join([COMPUTE_URL_BASE, 'projects/', project, '/zones/', zone, '/', collection, '/', name])


def RegionalComputeUrl(project, region, collection, name):
  """Generate regional compute URL."""
  return ''.join([COMPUTE_URL_BASE, 'projects/', project, '/regions/', region, '/', collection, '/', name])


def GenerateConfig(context):
  """Generate configuration."""

  # Get/generate variables from context
  zone = context.properties['zone']
  project = context.env['project']
  instance_name = context.properties['instanceName']
  instance_type = ZonalComputeUrl(project, zone, 'machineTypes', context.properties['instanceType'])
  region = context.properties['zone'][:context.properties['zone'].rfind('-')]
  linux_image_project = context.properties['linuxImageProject']
  linux_image = GlobalComputeUrl(linux_image_project, 'images', context.properties['linuxImage'])
  deployment_script_location = str(context.properties.get('deployment_script_location', 'https://storage.googleapis.com/sapdeploy/dm-templates'))
  primary_startup_url = "curl " + deployment_script_location + "/sap_maxdb/startup.sh | bash -s " + deployment_script_location
  network_tags = { "items": str(context.properties.get('networkTag', '')).split(',') if len(str(context.properties.get('networkTag', ''))) else [] }
  service_account = str(context.properties.get('serviceAccount', context.env['project_number'] + '-compute@developer.gserviceaccount.com'))

  ## Get deployment template specific variables from context
  maxdb_sid = str(context.properties.get('maxdbSID', ''))
  maxdb_root_size = context.properties['maxdbRootSize']
  maxdb_data_size = context.properties['maxdbDataSize']
  maxdb_log_size = context.properties['maxdbLogSize']
  maxdb_log_ssd = str(context.properties['maxdbLogSSD'])
  maxdb_data_size = context.properties['maxdbDataSize']
  maxdb_data_ssd = str(context.properties['maxdbDataSSD'])
  maxdb_backup_size = context.properties['maxdbBackupSize']
  usrsap_size = context.properties['usrsapSize']
  sapmnt_size = context.properties['sapmntSize']
  swap_size = context.properties['swapSize']
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

  ## determine disk types
  if maxdb_data_ssd == "True":
      maxdb_data_type = "pd-ssd"
  else:
      maxdb_data_type = "pd-standard"

  if maxdb_log_ssd== "True":
      maxdb_log_type = "pd-ssd"
  else:
      maxdb_log_type = "pd-standard"

  # set startup URL
  if sap_deployment_debug == "True":
      primary_startup_url = primary_startup_url + " -x"

  # compile complete json
  sap_node = []
  disks = []

  # /
  disks.append({'deviceName': 'boot',
                'type': 'PERSISTENT',
                'boot': True,
                'autoDelete': True,
                'initializeParams': {
                      'diskName': instance_name + '-boot',
                      'sourceImage': linux_image,
                      'diskSizeGb': '30'
                }
               })

  # /sapdb
  sap_node.append({
          'name': instance_name + '-maxdbroot',
          'type': 'compute.v1.disk',
          'properties': {
              'zone': zone,
              'sizeGb': maxdb_root_size,
              'type': ZonalComputeUrl(project, zone, 'diskTypes','pd-standard')
          }
          })
  disks.append({'deviceName': instance_name + '-maxdbroot',
              'type': 'PERSISTENT',
              'source': ''.join(['$(ref.', instance_name + '-maxdbroot', '.selfLink)']),
              'autoDelete': True
               })

  # /sapdb/SID/saplog
  sap_node.append({
          'name': instance_name + '-maxdblog',
          'type': 'compute.v1.disk',
          'properties': {
              'zone': zone,
              'sizeGb': maxdb_log_size,
              'type': ZonalComputeUrl(project, zone, 'diskTypes',maxdb_log_type)
          }
          })
  disks.append({'deviceName': instance_name + '-maxdblog',
              'type': 'PERSISTENT',
              'source': ''.join(['$(ref.', instance_name + '-maxdblog', '.selfLink)']),
              'autoDelete': True
               })

  # /sapdb/SID/sapdata
  sap_node.append({
          'name': instance_name + '-maxdbdata',
          'type': 'compute.v1.disk',
          'properties': {
              'zone': zone,
              'sizeGb': maxdb_data_size,
              'type': ZonalComputeUrl(project, zone, 'diskTypes',maxdb_data_type)
          }
          })
  disks.append({'deviceName': instance_name + '-maxdbdata',
              'type': 'PERSISTENT',
              'source': ''.join(['$(ref.', instance_name + '-maxdbdata', '.selfLink)']),
              'autoDelete': True
               })

  # /maxdbbackup
  sap_node.append({
          'name': instance_name + '-maxdbbackup',
          'type': 'compute.v1.disk',
          'properties': {
              'zone': zone,
              'sizeGb': maxdb_backup_size,
              'type': ZonalComputeUrl(project, zone, 'diskTypes','pd-standard')
          }
          })
  disks.append({'deviceName': instance_name + '-maxdbbackup',
              'type': 'PERSISTENT',
              'source': ''.join(['$(ref.', instance_name + '-maxdbbackup', '.selfLink)']),
              'autoDelete': True
               })

  # OPTIONAL - /usr/sap
  if usrsap_size > 0:
      sap_node.append({
              'name': instance_name + '-usrsap',
              'type': 'compute.v1.disk',
              'properties': {
                  'zone': zone,
                  'sizeGb': usrsap_size,
                  'type': ZonalComputeUrl(project, zone, 'diskTypes','pd-standard')
              }
              })
      disks.append({'deviceName': instance_name + '-usrsap',
                  'type': 'PERSISTENT',
                  'source': ''.join(['$(ref.', instance_name + '-usrsap', '.selfLink)']),
                  'autoDelete': True
                   })
  # OPTIONAL - /sapmnt
  if sapmnt_size > 0:
      sap_node.append({
              'name': instance_name + '-sapmnt',
              'type': 'compute.v1.disk',
              'properties': {
                  'zone': zone,
                  'sizeGb': sapmnt_size,
                  'type': ZonalComputeUrl(project, zone, 'diskTypes','pd-standard')
              }
          })
      disks.append({'deviceName': instance_name + '-sapmnt',
                  'type': 'PERSISTENT',
                  'source': ''.join(['$(ref.', instance_name + '-sapmnt', '.selfLink)']),
                  'autoDelete': True
                   })

  # OPTIONAL - swap disk
  if swap_size > 0:
      sap_node.append({
              'name': instance_name + '-swap',
              'type': 'compute.v1.disk',
              'properties': {
                  'zone': zone,
                  'sizeGb': swap_size,
                  'type': ZonalComputeUrl(project, zone, 'diskTypes','pd-standard')
              }
              })
      disks.append({'deviceName': instance_name + '-swap',
                  'type': 'PERSISTENT',
                  'source': ''.join(['$(ref.', instance_name + '-swap', '.selfLink)']),
                  'autoDelete': True
                   })

  # VM instance
  sap_node.append({
          'name': instance_name,
          'type': 'compute.v1.instance',
          'properties': {
              'zone': zone,
              'minCpuPlatform': 'Automatic',
              'machineType': instance_type,
              'metadata': {
                  'items': [{
                      'key': 'startup-script',
                      'value': primary_startup_url
                  },
                  {
                      'key': 'post_deployment_script',
                      'value': post_deployment_script
                  },                     
                  {
                      'key': 'sap_maxdb_sid',
                      'value': maxdb_sid
                  },
                  {
                      'key': 'sap_deployment_debug',
                      'value': sap_deployment_debug
                  }]
              },
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
                  }],
              "tags": network_tags,
              'disks': disks
              }
          })

  return {'resources': sap_node}
