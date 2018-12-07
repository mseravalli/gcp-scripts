#!/usr/bin/env python3

import googleapiclient.discovery
import subprocess
import time

# Documentation available under:
# https://developers.google.com/resources/api-libraries/documentation/compute/v1/python/latest/index.html

# In order to work properly the application needs to have access to the env
# variable GOOGLE_APPLICATION_CREDENTIALS that will store the absolute path
# of the credential:
# $ export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/sa-hana-installer.json

project="sandbox-303kdn50"
network_name="default"
subnet="default"
region = "europe-west4"
zone = region+"-c"
sys_nr="36"
passwd="hUk27d.er20"
instance_name="marcosturfdonttuch"
worker = instance_name + 'w1'
new_worker = instance_name + 'w2'

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
    
    time.sleep(2)

def stop_hana():
  subprocess.call('./hana_stop.sh')
  print(f'hana stopped')

def start_hana():
  return 

def add_hana_node():
  subprocess.call('./hana_add_node.sh')
  print(f'hana node added')

# copy the worker
def stop_worker():
  op = compute.instances().stop(project=project, zone=zone, instance=worker).execute()
  wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])
  print(f'worker {worker} stopped')

def start_worker():
  op = compute.instances().start(project=project, zone=zone, instance=worker).execute()
  wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])
  print(f'worker {worker} started')

def create_worker_snapshot():
  try:
    compute.snapshots().get(project=project, snapshot=instance_name + '-worker-boot').execute()
    print('snaphost is already present won\'t be created')
    return 
  except googleapiclient.errors.HttpError:
    print('snaphost will be created')
  except:
    print('error calling the API will exit')
    return 

  stop_worker()
  operations = []
  body ={
    'name': instance_name + '-worker-boot'
  } 
  disk = worker + '-boot'
  op = compute.disks().createSnapshot(project=project, body=body, zone=zone, disk=disk).execute()
  operations.append(op)

  body ={
    'name': instance_name + '-worker-pdssd'
  } 
  disk = worker + '-pdssd'
  op = compute.disks().createSnapshot(project=project, body=body, zone=zone, disk=disk).execute()
  operations.append(op)

  for op in operations:
    wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])

  start_worker()
  print('disks copied')

def create_disks_for_new_worker():
  # TODO skip if the disks are already present
  operations = []
  body ={
    "type": "projects/sandbox-303kdn50/zones/europe-west4-c/diskTypes/pd-ssd", 
    "sourceSnapshot": 'projects/sandbox-303kdn50/global/snapshots/'+ instance_name + '-worker-boot',
    "autoDelete": True,
    "name": new_worker+'-boot'
  } 
  op = compute.disks().insert(project=project, body=body, zone=zone).execute()
  operations.append(op)

  body ={
    "type": "projects/sandbox-303kdn50/zones/europe-west4-c/diskTypes/pd-ssd", 
    "sourceSnapshot": 'projects/sandbox-303kdn50/global/snapshots/'+ instance_name + '-worker-pdssd',
    "autoDelete": True,
    "name": new_worker+'-pdssd'
  } 
  op = compute.disks().insert(project=project, body=body, zone=zone).execute()
  operations.append(op)

  for op in operations:
    wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])
  print('new disks created')

def create_new_worker():
  worker_description = compute.instances() \
    .get(project=project, zone=zone, instance=worker).execute()

  new_worker_description = {}
  new_worker_description['name'] = new_worker
  new_worker_description["zone"] = worker_description["zone"]
  new_worker_description["machineType"] = worker_description["machineType"]
  new_worker_description["network"] = worker_description["networkInterfaces"][0]["network"]
  new_worker_description["subnetwork"] = worker_description["networkInterfaces"][0]["subnetwork"]
  new_worker_description["disks"] = [{
    'deviceName': new_worker+'-boot',
    'source': f'https://www.googleapis.com/compute/v1/projects/sandbox-303kdn50/zones/europe-west4-c/disks/{new_worker}-boot',
    'boot': True
  },{
    'deviceName': new_worker+'-pdssd',
    'source': f'https://www.googleapis.com/compute/v1/projects/sandbox-303kdn50/zones/europe-west4-c/disks/{new_worker}-pdssd',
    'boot': False
  }]

  new_worker_description["networkInterfaces"] = [
    { 
      "network": new_worker_description["network"],
      "subnetwork": new_worker_description["subnetwork"],
      "accessConfigs": [ 
        {
          "name": "External NAT",
          "type": "ONE_TO_ONE_NAT",
        },
      ],
    },
  ]

  op = compute.instances().insert(project=project, zone=zone, body=new_worker_description).execute()
  wait_for_operation(compute, project, zone, op['name'])
  print(f'new worker {new_worker_description["name"]} created')

# acutal work :)
stop_hana()
create_worker_snapshot()
create_disks_for_new_worker()
create_new_worker()
time.sleep(10)
add_hana_node()
