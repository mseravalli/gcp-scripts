#!/usr/bin/env python3

""" Reprovisions the provided VM. """

import time
from absl import app
from absl import flags
import googleapiclient.discovery

# Documentation available under:
# https://developers.google.com/resources/api-libraries/documentation/compute/v1/python/latest/index.html

# In order to work properly the application needs to have access to the env
# variable GOOGLE_APPLICATION_CREDENTIALS that will store the absolute path
# of the credential:
# $ export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/sa-hana-operator.json


FLAGS = flags.FLAGS

flags.DEFINE_string("project",
                    None,
                    "Project id that needs to be changed.")
flags.mark_flag_as_required("project")

flags.DEFINE_string("zone",
                    None,
                    "Zone where the resources are deployed.")
flags.mark_flag_as_required("zone")

flags.DEFINE_string("original_vm_name",
                    None,
                    "VM that needs to be reprovisioned.")
flags.mark_flag_as_required("original_vm_name")

flags.DEFINE_string("new_MachineType",
                    None,
                    "New Type of the VM.")
flags.mark_flag_as_required("new_MachineType")


def wait_for_operation(compute, project, zone, operation):
  """Waits for the passed operation to be finished and then returns."""

  while True:
    result = compute.zoneOperations().get(
        project=project,
        zone=zone,
        operation=operation
    ).execute()

    if result["status"] == "DONE":
      if "error" in result:
        raise Exception(result["error"])
      return result

    time.sleep(2)


def main(argv):
  del argv # unused

  print("yolo")

  project = FLAGS.project
  zone = FLAGS.zone
  original_vm_name = FLAGS.original_vm_name
  new_MachineType = FLAGS.new_MachineType

  compute = googleapiclient.discovery.build("compute", "v1")

  original_vm = compute.instances() \
    .get(project=project, zone=zone, instance=original_vm_name).execute()

  print(original_vm)

  # copy original settings
  cloned_vm = original_vm
  cloned_vm["machineType"] = f"{cloned_vm['zone']}/machineTypes/{new_MachineType}"
  cloned_vm["networkInterfaces"] = [{
      "network": original_vm["networkInterfaces"][0]["network"],
      "subnetwork": original_vm["networkInterfaces"][0]["subnetwork"],
      "accessConfigs": [
          {
              "name": "External NAT",
              "type": "ONE_TO_ONE_NAT",
          },
      ],
  }]

  # TODO store this configuration on disk in case of issues
  print("vm setting copied")

  # don't delete disks at VM deletion
  for disk in original_vm["disks"]:
    op = compute.instances() \
      .setDiskAutoDelete(project=project,
                         zone=zone,
                         instance=original_vm_name,
                         autoDelete=False,
                         deviceName=disk["deviceName"]) \
      .execute()
    wait_for_operation(compute, project, zone, op["name"])

  print("disks won't be deleted")

  op = compute.instances().delete(
      project=project,
      zone=zone,
      instance=original_vm_name
  ).execute()
  wait_for_operation(compute, project, zone, op["name"])

  print("vm deleted")

  op = compute.instances().insert(
      project=project,
      zone=zone,
      body=cloned_vm
  ).execute()

  wait_for_operation(compute, project, zone, op["name"])
  print("vm cloned")

if __name__ == "__main__":
  app.run(main)
