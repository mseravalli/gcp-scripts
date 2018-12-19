#!/usr/bin/env python3

""" Adds a new node to hana. """

import subprocess
import time
from absl import app
from absl import flags
import googleapiclient.discovery

# Documentation available under:
# https://developers.google.com/resources/api-libraries/documentation/compute/v1/python/latest/index.html

# In order to work properly the application needs to have access to the env
# variable GOOGLE_APPLICATION_CREDENTIALS that will store the absolute path
# of the credential:
# $ export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/sa-hana-installer.json


FLAGS = flags.FLAGS

flags.DEFINE_string("project",
                    None,
                    "")
flags.mark_flag_as_required("project")

flags.DEFINE_string("zone",
                    None,
                    "")
flags.mark_flag_as_required("zone")

flags.DEFINE_string("worker",
                    None,
                    "")
flags.mark_flag_as_required("worker")

flags.DEFINE_string("new_worker",
                    None,
                    "")
flags.mark_flag_as_required("new_worker")

def wait_for_operation(compute, project, zone, operation):
  """Waits for GCP operation to finish."""

  while True:
    result = compute.zoneOperations().get(
        project=project,
        zone=zone,
        operation=operation
    ).execute()

    if result['status'] == 'DONE':
      if 'error' in result:
        raise Exception(result['error'])
      return result

    time.sleep(2)

def stop_hana():
  """Stops hana."""

  subprocess.call('./hana_stop.sh')
  print(f'hana stopped')

def start_hana():
  """Starts hana."""

  return

def add_hana_node():
  """Adds hana node."""

  subprocess.call('./hana_add_node.sh')
  print(f'hana node added')

def stop_worker(compute, project, zone, worker):
  """Stops worker."""

  op = compute.instances().stop(project=project, zone=zone, instance=worker).execute()
  wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])
  print(f'worker {worker} stopped')

def start_worker(compute, project, zone, worker):
  """Starts worker."""

  op = compute.instances().start(project=project, zone=zone, instance=worker).execute()
  wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])
  print(f'worker {worker} started')

def create_worker_snapshot(compute, project, zone, worker):
  """Creates a snapshot for the worker if it does not already exists."""

  try:
    compute.snapshots().get(project=project, snapshot=worker + '-worker-boot').execute()
    print('snaphost is already present won\'t be created')
    return
  except googleapiclient.errors.HttpError:
    print('snaphost will be created')
  except:
    print('error calling the API will exit')
    return

  stop_worker(compute=compute, project=project, zone=zone, worker=worker)
  operations = []
  body = {
      "name": f"{worker}-worker-boot"
  }
  disk = f"{worker}-boot"
  op = compute.disks().createSnapshot(
      project=project,
      body=body,
      zone=zone,
      disk=disk
  ).execute()
  operations.append(op)

  body = {
      'name': worker + '-worker-pdssd'
  }
  disk = worker + '-pdssd'
  op = compute.disks().createSnapshot(
      project=project,
      body=body,
      zone=zone,
      disk=disk
  ).execute()
  operations.append(op)

  for op in operations:
    wait_for_operation(
        compute=compute,
        project=project,
        zone=zone,
        operation=op['name']
    )

  start_worker(compute=compute, project=project, zone=zone, worker=worker)
  print('disks copied')

def create_disks_for_new_worker(compute, project, zone, new_worker, worker):
  """Creates disks for new worker."""

  # TODO skip if the disks are already present
  operations = []
  body = {
      "type": f"projects/{project}/zones/europe-west4-c/diskTypes/pd-ssd",
      "sourceSnapshot": f"projects/{project}/global/snapshots/{worker}-worker-boot",
      "autoDelete": True,
      "name": f"{new_worker}-boot"
  }
  op = compute.disks().insert(project=project, body=body, zone=zone).execute()
  operations.append(op)

  body = {
      "type": f"projects/{project}/zones/europe-west4-c/diskTypes/pd-ssd",
      "sourceSnapshot": f"projects/{project}/global/snapshots/{worker}-worker-pdssd",
      "autoDelete": True,
      "name": f"{new_worker}-pdssd"
  }
  op = compute.disks().insert(project=project, body=body, zone=zone).execute()
  operations.append(op)

  for op in operations:
    wait_for_operation(compute=compute, project=project, zone=zone, operation=op['name'])
  print('new disks created')

def create_new_worker(compute, project, zone, worker, new_worker):
  """Creates a new worker."""

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
      'source': f'https://www.googleapis.com/compute/v1/projects/{project}/zones/europe-west4-c/disks/{new_worker}-boot',
      'autoDelete': True,
      'boot': True
  }, {
      'deviceName': new_worker+'-pdssd',
      'source': f'https://www.googleapis.com/compute/v1/projects/{project}/zones/europe-west4-c/disks/{new_worker}-pdssd',
      'autoDelete': True,
      'boot': False
  }]

  new_worker_description["networkInterfaces"] = [{
      "network": new_worker_description["network"],
      "subnetwork": new_worker_description["subnetwork"],
      "accessConfigs": [{
          "name": "External NAT",
          "type": "ONE_TO_ONE_NAT",
      }]
  }]

  op = compute.instances().insert(project=project, zone=zone, body=new_worker_description).execute()
  wait_for_operation(compute, project, zone, op['name'])
  print(f'new worker {new_worker_description["name"]} created')

def main(argv):
  """Main program."""

  del argv # unused

  project = FLAGS.project
  zone = FLAGS.zone
  worker = FLAGS.worker
  new_worker = FLAGS.new_worker

  compute = googleapiclient.discovery.build('compute', 'v1')

  stop_hana()
  create_worker_snapshot(compute=compute, project=project, zone=zone, worker=worker)
  create_disks_for_new_worker(compute=compute, project=project, zone=zone, worker=worker, new_worker=new_worker)
  create_new_worker(compute=compute, project=project, zone=zone, worker=worker, new_worker=new_worker)

  # for real production usage this threshold need to be validated
  # TODO: create a function that waits until hana is up and running
  time.sleep(300)
  add_hana_node()

if __name__ == "__main__":
  app.run(main)
