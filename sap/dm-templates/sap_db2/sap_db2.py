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
  primary_startup_url = "curl " + deployment_script_location + "/sap_db2/startup.sh | bash -s " + deployment_script_location
  network_tags = { "items": str(context.properties.get('networkTag', '')).split(',') if len(str(context.properties.get('networkTag', ''))) else [] }
  service_account = str(context.properties.get('serviceAccount', context.env['project_number'] + '-compute@developer.gserviceaccount.com'))

  # Get deployment template specific variables from context
  db2_sid = str(context.properties.get('db2SID', ''))
  db2sid_size = context.properties['db2sidSize']
  db2home_size = context.properties['db2homeSize']
  db2dump_size  = context.properties['db2dumpSize']
  db2saptmp_size = context.properties['db2saptmpSize']
  db2log_size = context.properties['db2logSize']
  db2log_ssd = str(context.properties['db2logSSD'])
  db2sapdata_size = context.properties['db2sapdataSize']
  db2sapdata_ssd = str(context.properties['db2sapdataSSD'])
  db2backup_size = context.properties['db2backupSize']
  usrsap_size = context.properties['usrsapSize']
  sapmnt_size = context.properties['sapmntSize']
  sap_deployment_debug = str(context.properties.get('sap_deployment_debug', 'False')) 
  post_deployment_script = str(context.properties.get('post_deployment_script', ''))
  other_host = str(context.properties.get('otherHost',''))
  swap_size = context.properties['swapSize']

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
  if db2sapdata_ssd == "True":
      db2sapdata_type = "pd-ssd"
  else:
      db2sapdata_type = "pd-standard"

  if db2log_ssd == "True":
      db2log_type = "pd-ssd"
  else:
      db2log_type = "pd-standard"

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

  # /db2/SID
  sap_node.append({
          'name': instance_name + '-db2sid',
          'type': 'compute.v1.disk',
          'properties': {
              'zone': zone,
              'sizeGb': db2sid_size,
              'type': ZonalComputeUrl(project, zone, 'diskTypes','pd-standard')
          }
          })
  disks.append({'deviceName': instance_name + '-db2sid',
              'type': 'PERSISTENT',
              'source': ''.join(['$(ref.', instance_name + '-db2sid', '.selfLink)']),
              'autoDelete': True
               })


  # /db2/SID/db2dump
  sap_node.append({
          'name': instance_name + '-db2dump',
          'type': 'compute.v1.disk',
          'properties': {
              'zone': zone,
              'sizeGb': db2dump_size,
              'type': ZonalComputeUrl(project, zone, 'diskTypes','pd-standard')
          }
          })
  disks.append({'deviceName': instance_name + '-db2dump',
              'type': 'PERSISTENT',
              'source': ''.join(['$(ref.', instance_name + '-db2dump', '.selfLink)']),
              'autoDelete': True
               })

  # /db2/db2<dbsid>
  sap_node.append({
                  'name': instance_name + '-db2home',
                  'type': 'compute.v1.disk',
                  'properties': {
                          'zone': zone,
                          'sizeGb': db2home_size,
                          'type': ZonalComputeUrl(project, zone, 'diskTypes','pd-standard')
                  }
                  })
                    
  disks.append({'deviceName': instance_name + '-db2home',
                          'type': 'PERSISTENT',
                          'source': ''.join(['$(ref.', instance_name + '-db2home', '.selfLink)']),
                          'autoDelete': True
                              })

  # /db2/SID/saptmp
  sap_node.append({
          'name': instance_name + '-db2saptmp',
          'type': 'compute.v1.disk',
          'properties': {
              'zone': zone,
              'sizeGb': db2saptmp_size,
              'type': ZonalComputeUrl(project, zone, 'diskTypes','pd-standard')
          }
          })

  disks.append({'deviceName': instance_name + '-db2saptmp',
              'type': 'PERSISTENT',
              'source': ''.join(['$(ref.', instance_name + '-db2saptmp', '.selfLink)']),
              'autoDelete': True
               })

  # /db2/SID/log_dir
  sap_node.append({
          'name': instance_name + '-db2log',
          'type': 'compute.v1.disk',
          'properties': {
              'zone': zone,
              'sizeGb': db2log_size,
              'type': ZonalComputeUrl(project, zone, 'diskTypes',db2log_type)
          }
          })
  disks.append({'deviceName': instance_name + '-db2log',
              'type': 'PERSISTENT',
              'source': ''.join(['$(ref.', instance_name + '-db2log', '.selfLink)']),
              'autoDelete': True
               })

  # /db2/SID/sapdata
  sap_node.append({
          'name': instance_name + '-db2sapdata',
          'type': 'compute.v1.disk',
          'properties': {
              'zone': zone,
              'sizeGb': db2sapdata_size,
              'type': ZonalComputeUrl(project, zone, 'diskTypes',db2sapdata_type)
          }
          })
  disks.append({'deviceName': instance_name + '-db2sapdata',
              'type': 'PERSISTENT',
              'source': ''.join(['$(ref.', instance_name + '-db2sapdata', '.selfLink)']),
              'autoDelete': True
               })

  # /db2backup
  sap_node.append({
          'name': instance_name + '-db2backup',
          'type': 'compute.v1.disk',
          'properties': {
              'zone': zone,
              'sizeGb': db2backup_size,
              'type': ZonalComputeUrl(project, zone, 'diskTypes','pd-standard')
          }
          })
  disks.append({'deviceName': instance_name + '-db2backup',
              'type': 'PERSISTENT',
              'source': ''.join(['$(ref.', instance_name + '-db2backup', '.selfLink)']),
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
                      'key': 'sap_ibm_db2_sid',
                      'value': db2_sid
                  },
                  {
                      'key': 'other_host',
                      'value': other_host
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
