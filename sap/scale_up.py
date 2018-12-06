#!/usr/bin/env python3

import googleapiclient.discovery
import time

# Documentation available under:
# https://developers.google.com/resources/api-libraries/documentation/compute/v1/python/latest/index.html

# In order to work properly the application needs to have access to the env
# variable GOOGLE_APPLICATION_CREDENTIALS that will store the absolute path
# of the credential:
# $ export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/sa-hana-installer.json

project = "sandbox-303kdn50"
region = "europe-west4"
zone = region+"-c"

original_vm_name = "sandbox-303kdn50-hana-vmw3"

compute = googleapiclient.discovery.build('compute', 'v1')

# [START wait_for_operation]
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

original_vm = compute.instances() \
  .get(project=project, zone=zone, instance=original_vm_name).execute()

# copy original settings
cloned_vm = {}
cloned_vm["name"] = original_vm_name
cloned_vm["zone"] = original_vm["zone"]
cloned_vm["machineType"] = cloned_vm["zone"] + "/machineTypes/n1-highmem-64"
cloned_vm["network"] = original_vm["networkInterfaces"][0]["network"]
cloned_vm["subnetwork"] = original_vm["networkInterfaces"][0]["subnetwork"]
cloned_vm["disks"] = original_vm["disks"]

cloned_vm["networkInterfaces"] = [
  { 
    "network": cloned_vm["network"],
    "subnetwork": cloned_vm["subnetwork"],
    "accessConfigs": [ 
      {
        "name": "External NAT",
        "type": "ONE_TO_ONE_NAT",
      },
    ],
  },
]

print("vm setting copied")

# don't delete disks at VM deletion
for d in original_vm["disks"]:
  op = compute.instances() \
    .setDiskAutoDelete(project=project,
                       zone=zone,
                       instance=original_vm_name,
                       autoDelete=False,
                       deviceName=d["deviceName"]) \
    .execute()
  wait_for_operation(compute, project, zone, op['name'])

print("disks won't be deleted")

op = compute.instances().delete(project=project, zone=zone, instance=original_vm_name).execute()
wait_for_operation(compute, project, zone, op['name'])

print("vm deleted")

op = compute.instances().insert(project=project, zone=zone, body=cloned_vm).execute()
wait_for_operation(compute, project, zone, op['name'])
print("vm cloned")



