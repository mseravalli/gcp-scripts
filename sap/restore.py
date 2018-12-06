#!/usr/bin/env python3

import googleapiclient.discovery
import time 

# Documentation available under:
# https://developers.google.com/resources/api-libraries/documentation/compute/v1/python/latest/index.html

# In order to work properly the application needs to have access to the env
# variable GOOGLE_APPLICATION_CREDENTIALS that will store the absolute path
# of the credential:
# $ export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/sa-hana-installer.json

# compute = googleapiclient.discovery.build('compute', 'v1')
# instances = compute.instances().list(project=project, zone=zone).execute()
# instances_name = [i['name'] for i in instances['items']]
# print(instances_name)

project="sandbox-303kdn50"
network_name="default"
subnet="default"
zone="europe-west4-c"
tag="sap-hana"
sys_nr="36"
passwd="hUk27d.er20"
instance_name="sape36vm"
backup_id="1544106061721"

compute = googleapiclient.discovery.build('compute', 'v1')

def wait_for_operation(compute, project, zone, operation):
  while True:
    result = compute.zoneOperations().get(
      project=project,
      zone=zone,
      operation=operation).execute()
    
    if result['status'] == 'DONE':
      if 'error' in result:
        raise Exception(result['error'])
      return result
    
    time.sleep(1)

instances = [
  instance_name + 'w1',
  instance_name + 'w2',
  instance_name
]

# create new disks name does not matter, matters how you mount them
for instance in instances: 
  body ={
    "type": "projects/sandbox-303kdn50/zones/europe-west4-c/diskTypes/pd-ssd", 
    "sourceSnapshot": 'projects/sandbox-303kdn50/global/snapshots/'+ instance+'-'+backup_id,
    "name": instance+'-pdssd-restored',
    "sizeGb": "1750" 
  } 
  op = compute.disks().insert(project=project, body=body, zone=zone).execute()
  wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])

# shutdown VM
for instance in instances: 
  op = compute.instances().stop(project=project, zone=zone, instance=instance).execute()
  wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])

# deatach disks from VMs
for instance in instances: 
  op = compute.instances().detachDisk(project=project, zone=zone, instance=instance, deviceName=instance+'-pdssd').execute()
  wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])

# attach disks from snapshots
for instance in instances: 
  body = {
    'deviceName': instance + '-pdssd',
    'boot': False,
    'source': 'projects/sandbox-303kdn50/zones/europe-west4-c/disks/' + instance + '-pdssd-restored'
  }
  op = compute.instances().attachDisk(project=project, zone=zone, instance=instance, body=body).execute()
  wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])

# start VM
for instance in instances: 
  op = compute.instances().start(project=project, zone=zone, instance=instance).execute()
  wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])
