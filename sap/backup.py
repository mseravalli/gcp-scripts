#!/usr/bin/env python3

import googleapiclient.discovery
import time
import os

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
instance_name="sape36vm"

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

# start hana snapshot mode
# echo "hdbsql -n ${VM_NAME}:3${SYS_NR}15 -u system -p ${PASSWD} \"BACKUP DATA CREATE SNAPSHOT\"" > tmp_cmd.sh
# gcloud compute ssh ${VM_NAME} -- "sudo su - e36adm " < tmp_cmd.sh
# echo " hdbsql -xaj -n ${VM_NAME}:3${SYS_NR}15 -u system -p ${PASSWD} \"SELECT BACKUP_ID FROM \"PUBLIC\".\"M_BACKUP_CATALOG\" WHERE ENTRY_TYPE_NAME = 'data snapshot' AND STATE_NAME = 'prepared' \" " > tmp_cmd.sh
# BACKUP_ID=$(gcloud compute ssh ${VM_NAME} -- " sudo su - e36adm" < tmp_cmd.sh)
# echo ${BACKUP_ID}
# os.system(f'gcloud compute ssh {instance_name} -- " sudo su - e36adm" < tmp_cmd.sh')

# TODO delete this
exit(0)

# take snaphosts of the disks
operations = []
for instance in instances: 
  body ={
    'name': instance + '-pdssd-snapshot'
  } 
  disk = instance + '-pdssd'
  op = compute.disks().createSnapshot(project=project, body=body, zone=zone, disk=disk).execute()
  operations.append(op)

for op in operations:
  wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])

# stop hana snapshot mode
# echo "hdbsql -n ${VM_NAME}:3${SYS_NR}15 -u system -p ${PASSWD} \"BACKUP DATA CLOSE SNAPSHOT BACKUP_ID ${BACKUP_ID} SUCCESSFUL 'gcpstorage'\" " > tmp_cmd.sh
# gcloud compute ssh ${VM_NAME} -- "sudo su - e36adm " < tmp_cmd.sh
#
# rm tmp_cmd.sh


