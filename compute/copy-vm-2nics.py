import googleapiclient.discovery
import time

# Documentation available under:
# https://developers.google.com/resources/api-libraries/documentation/compute/v1/python/latest/index.html

# In order to work properly the application needs to have access to the env
# variable GOOGLE_APPLICATION_CREDENTIALS that will store the absolute path
# of the credential:
# $ export GOOGLE_APPLICATION_CREDENTIALS=$(pwd)/sa-python.json

# compute = googleapiclient.discovery.build('compute', 'v1')
# instances = compute.instances().list(project=project, zone=zone).execute()
# instances_name = [i['name'] for i in instances['items']]
# print(instances_name)

project = "test-seravalli-199408"
region = "europe-west1"
zone = region+"-c"

disk_type = "pd-standard"

attached_disk_name_1=f"google-{disk_type}-{int(time.time()*1E7)}"
attached_disk_name_2=f"google-{disk_type}-{int(time.time()*1E7)}"

original_vm_name = f"original-vm-{int(time.time()*1E7)}"

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

original_vm_config = {
  "name": original_vm_name,
  "zone": zone,
  "machineType": f"zones/{zone}/machineTypes/n1-standard-4",
  "networkInterfaces": [ 
    { 
      "network": "global/networks/default",
      "subnetwork": f"regions/{region}/subnetworks/default", 
      "accessConfigs": [ 
        {
          "name": "External NAT",
          "type": "ONE_TO_ONE_NAT",
        },
      ],
    },
  ],
  "disks": [
    { 
      "deviceName": f"os-disk-{original_vm_name}",
      "initializeParams": {
        "diskName": f"os-disk-{original_vm_name}",
        "diskType": f"zones/{zone}/diskTypes/{disk_type}",
        "diskSizeGb": "20", 
        "sourceImage": "projects/debian-cloud/global/images/family/debian-8",
      },
      "autoDelete": True,
      "boot": True,
      "mode": "READ_WRITE",
      "type": "PERSISTENT", 
    },
    { 
      "deviceName": attached_disk_name_1,
      "initializeParams": {
        "diskName": attached_disk_name_1,
        "diskType": f"zones/{zone}/diskTypes/{disk_type}",
        "diskSizeGb": "20", 
      },
      "autoDelete": True,
      "boot": False,
      "mode": "READ_WRITE",
      "type": "PERSISTENT", 
    },
    { 
      "deviceName": attached_disk_name_2,
      "initializeParams": {
        "diskName": attached_disk_name_2,
        "diskType": f"zones/{zone}/diskTypes/{disk_type}",
        "diskSizeGb": "20", 
      },
      "autoDelete": True,
      "boot": False,
      "mode": "READ_WRITE",
      "type": "PERSISTENT", 
    },
  ],
  "metadata": { 
    "items": [
      {
        "key": "startup-script",
        "value": f"""#! /bin/bash
          yes | sudo mkfs.ext3 /dev/disk/by-id/{attached_disk_name_1}
          sudo mkdir -p /mnt/disks/{attached_disk_name_1}
          sudo mount /dev/disk/by-id/{attached_disk_name_1} \
            /mnt/disks/{attached_disk_name_1}
          sudo chmod 777 -R /mnt/disks/{attached_disk_name_1}
          echo 'hello' > /mnt/disks/{attached_disk_name_1}/hello1.txt

          yes | sudo mkfs.ext3 /dev/disk/by-id/{attached_disk_name_2}
          sudo mkdir -p /mnt/disks/{attached_disk_name_2}
          sudo mount /dev/disk/by-id/{attached_disk_name_2} \
            /mnt/disks/{attached_disk_name_2}
          sudo chmod 777 -R /mnt/disks/{attached_disk_name_2}
          echo 'hello' > /mnt/disks/{attached_disk_name_2}/hello2.txt
        """
      },
    ],
  },
}

compute = googleapiclient.discovery.build('compute', 'v1')
op = compute.instances().insert(project=project, zone=zone, body=original_vm_config).execute()
wait_for_operation(compute, project, zone, op['name'])
print("vm created")

original_vm = compute.instances() \
  .get(project=project, zone=zone, instance=original_vm_name).execute()

# copy original settings
cloned_vm_type = original_vm["machineType"]
cloned_vm_zone = original_vm["zone"]
cloned_vm_subnetwork = original_vm["networkInterfaces"][0]["subnetwork"]
cloned_vm_attached_disks = [d for d in original_vm["disks"] if not d["boot"]]
cloned_vm_boot_disk = [d for d in original_vm["disks"] if d["boot"]][0]

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

print("vm setting copied")

op = compute.instances().delete(project=project, zone=zone, instance=original_vm_name).execute()
wait_for_operation(compute, project, zone, op['name'])

print("vm deleted")

cloned_vm_name = f"cloned-vm-{int(time.time()*1E7)}"

cloned_vm_startup_script="""#! /bin/bash"""
for d in cloned_vm_attached_disks:
  cloned_vm_startup_script=f"""{cloned_vm_startup_script} 
    sudo mkdir -p /mnt/disks/{d['deviceName']} ;
    sudo mount /dev/disk/by-id/{d['deviceName']} /mnt/disks/{d['deviceName']}
    sudo chmod 777 -R /mnt/disks/{d['deviceName']} ;
  """

cloned_vm_config = {
  "name": cloned_vm_name,
  "zone": zone,
  "machineType": f"zones/{zone}/machineTypes/n1-standard-4",
  "networkInterfaces": [ 
    { 
      "network": "global/networks/default",
      "subnetwork": f"regions/{region}/subnetworks/default", 
      "accessConfigs": [ 
        {
          "name": "External NAT",
          "type": "ONE_TO_ONE_NAT",
        },
      ],
    },
  ],
  "disks": original_vm["disks"],
  "metadata": { 
    "items": [
      {
        "key": "startup-script",
        "value": cloned_vm_startup_script
      },
    ],
  },
}

op = compute.instances().insert(project=project, zone=zone, body=cloned_vm_config).execute()
wait_for_operation(compute, project, zone, op['name'])
print("vm cloned")



